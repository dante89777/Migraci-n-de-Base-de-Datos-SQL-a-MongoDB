from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import check_password_hash

app = Flask(__name__)
CORS(app)

cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["InventoryOptimizer"]

SUCURSALES = {
    1: "Sucursal Centro",
    2: "Sucursal Sur",
    3: "Sucursal Norte",
    4: "Sucursal Valparaíso",
    5: "Sucursal Concepción",
}


def limpiar(doc):
    doc["_id"] = str(doc["_id"])
    return doc


# ==========================================================
# LOGIN
# ==========================================================
@app.route("/api/login", methods=["POST"])
def login():
    datos = request.get_json() or {}
    usuario = datos.get("usuario", "").strip()
    password = datos.get("password", "")

    user = db.usuarios.find_one({"usuario": usuario})

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    return jsonify({
        "usuario": user["usuario"],
        "nombre": user["nombre"],
        "rol": user["rol"],
        "sucursal_id": user.get("sucursal_id"),
    })


# ==========================================================
# PRODUCTOS
# ==========================================================
@app.route("/api/productos", methods=["GET"])
def obtener_productos():
    return jsonify([limpiar(p) for p in db.productos.find()])


@app.route("/api/productos", methods=["POST"])
def crear_producto():
    datos = request.get_json()
    ultimo = db.productos.find_one(sort=[("sku_id", -1)])
    nuevo_id = (ultimo["sku_id"] + 1) if ultimo else 1

    producto = {
        "sku_id": nuevo_id,
        "nombre": datos.get("nombre", ""),
        "categoria": datos.get("categoria", ""),
        "precio_costo": datos.get("precio_costo", 0),
        "precio_venta": datos.get("precio_venta", 0),
        "stock_minimo": datos.get("stock_minimo", 0),
        "stock_maximo": datos.get("stock_maximo", 0),
    }
    db.productos.insert_one(producto)
    return jsonify(limpiar(producto)), 201


@app.route("/api/productos/<int:sku_id>", methods=["DELETE"])
def eliminar_producto(sku_id):
    resultado = db.productos.delete_one({"sku_id": sku_id})
    if resultado.deleted_count == 0:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify({"mensaje": "Producto eliminado"})


# ==========================================================
# INVENTARIO
# ==========================================================
@app.route("/api/inventario", methods=["GET"])
def obtener_inventario():
    inventarios = []
    for inv in db.inventario.find():
        inv = limpiar(inv)
        inv["sucursal_nombre"] = SUCURSALES.get(inv.get("sucursal_id"), "Desconocida")
        inventarios.append(inv)
    return jsonify(inventarios)


# Registrar un movimiento de stock (push de transacción + ajuste de cantidad_disponible)
# Esto es lo que usa el rol "reponedor" al agregar o retirar productos del mapa
@app.route("/api/inventario/<int:sucursal_id>/<int:sku_id>/movimiento", methods=["POST"])
def registrar_movimiento(sucursal_id, sku_id):
    datos = request.get_json() or {}
    tipo = datos.get("tipo")
    cantidad = datos.get("cantidad", 0)
    motivo = datos.get("motivo", "Reposición de tienda")

    if tipo not in ("entrada", "salida"):
        return jsonify({"error": "tipo debe ser 'entrada' o 'salida'"}), 400
    try:
        cantidad = int(cantidad)
    except (TypeError, ValueError):
        return jsonify({"error": "cantidad debe ser un número"}), 400
    if cantidad <= 0:
        return jsonify({"error": "cantidad debe ser mayor a 0"}), 400

    transaccion = {
        "tipo": tipo,
        "cantidad": cantidad,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "motivo": motivo,
    }

    cambio = cantidad if tipo == "entrada" else -cantidad

    resultado = db.inventario.update_one(
        {"sucursal_id": sucursal_id, "sku_id": sku_id},
        {
            "$push": {"transacciones": transaccion},
            "$inc": {"cantidad_disponible": cambio},
        },
    )

    if resultado.matched_count == 0:
        return jsonify({"error": "No existe inventario para esa sucursal/producto"}), 404

    return jsonify({"mensaje": "Movimiento registrado", "transaccion": transaccion}), 201


# ==========================================================
# TRANSACCIONES (aplanadas, para el rol gerente)
# ==========================================================
@app.route("/api/transacciones", methods=["GET"])
def obtener_transacciones():
    productos_map = {p["sku_id"]: p for p in db.productos.find()}
    resultado = []

    for inv in db.inventario.find():
        producto = productos_map.get(inv["sku_id"])
        nombre_producto = producto["nombre"] if producto else f"SKU {inv['sku_id']}"

        for t in inv.get("transacciones", []):
            resultado.append({
                "sucursal_id": inv["sucursal_id"],
                "sucursal_nombre": SUCURSALES.get(inv["sucursal_id"], "Desconocida"),
                "producto": nombre_producto,
                "tipo": t["tipo"],
                "cantidad": t["cantidad"],
                "fecha": t["fecha"],
                "motivo": t["motivo"],
            })

    resultado.sort(key=lambda x: x["fecha"], reverse=True)
    return jsonify(resultado)


# ==========================================================
# GANANCIAS POR SUCURSAL (rol gerente)
# Se calcula como: suma de (cantidad vendida en transacciones tipo "salida" x precio_venta)
# ==========================================================
@app.route("/api/ganancias", methods=["GET"])
def obtener_ganancias():
    productos_map = {p["sku_id"]: p for p in db.productos.find()}
    ingresos = {sid: 0 for sid in SUCURSALES}

    for inv in db.inventario.find():
        producto = productos_map.get(inv["sku_id"])
        if not producto:
            continue
        for t in inv.get("transacciones", []):
            if t.get("tipo") == "salida":
                ingresos[inv["sucursal_id"]] = (
                    ingresos.get(inv["sucursal_id"], 0) + t["cantidad"] * producto["precio_venta"]
                )

    resultado = [
        {"sucursal_id": sid, "sucursal_nombre": nombre, "ingresos_totales": ingresos.get(sid, 0)}
        for sid, nombre in SUCURSALES.items()
    ]
    return jsonify(resultado)


# ==========================================================
# ESTADÍSTICAS GENERALES
# ==========================================================
@app.route("/api/estadisticas", methods=["GET"])
def obtener_estadisticas():
    total_productos = db.productos.count_documents({})
    total_inventarios = db.inventario.count_documents({})
    total_transacciones = sum(len(inv.get("transacciones", [])) for inv in db.inventario.find())

    return jsonify({
        "productos": total_productos,
        "inventarios": total_inventarios,
        "transacciones": total_transacciones,
        "sucursales": len(SUCURSALES),
    })


if __name__ == "__main__":
    print("API corriendo en http://localhost:5000")
    app.run(debug=True, port=5000)