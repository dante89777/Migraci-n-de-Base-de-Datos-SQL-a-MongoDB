import random
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

# Zonas del mapa (deben calzar con los id="" del SVG en el front-end)
ZONAS_MAPA = [
    "zona-lacteos", "zona-congelados", "zona-bebidas", "zona-refrigerios",
    "zona-golosinas", "zona-alcohol", "zona-condimentos", "zona-conservas",
    "zona-panaderia",
]

HORA_LIMITE = "09:15:00"  # después de esta hora, se marca "Atrasado"


def limpiar(doc):
    doc["_id"] = str(doc["_id"])
    return doc


def hoy():
    return datetime.now().strftime("%Y-%m-%d")


def ahora():
    return datetime.now().strftime("%H:%M:%S")


# ==========================================================
# LOGIN / LOGOUT + ASISTENCIA
# ==========================================================
@app.route("/api/login", methods=["POST"])
def login():
    datos = request.get_json() or {}
    usuario = datos.get("usuario", "").strip()
    password = datos.get("password", "")
    nombre = datos.get("nombre", "").strip()
    apellido = datos.get("apellido", "").strip()
    sucursal_id = datos.get("sucursal_id")

    if not nombre or not apellido or not sucursal_id:
        return jsonify({"error": "Nombre, apellido y sucursal son obligatorios"}), 400

    user = db.usuarios.find_one({"usuario": usuario})
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    sucursal_id = int(sucursal_id)
    rol = user["rol"]

    zona_asignada = random.choice(ZONAS_MAPA) if rol == "seguridad" else None

    registro = {
        "usuario": usuario,
        "nombre": nombre,
        "apellido": apellido,
        "rol": rol,
        "sucursal_id": sucursal_id,
        "fecha": hoy(),
        "hora_entrada": ahora(),
        "hora_salida": None,
        "zona_asignada": zona_asignada,
    }

    # upsert: si la misma persona ya había entrado hoy, se actualiza en vez de duplicar
    resultado = db.asistencia.update_one(
        {"usuario": usuario, "nombre": nombre, "apellido": apellido, "fecha": hoy()},
        {"$set": registro},
        upsert=True,
    )

    asistencia_id = (
        str(resultado.upserted_id)
        if resultado.upserted_id
        else str(db.asistencia.find_one({"usuario": usuario, "nombre": nombre, "apellido": apellido, "fecha": hoy()})["_id"])
    )

    return jsonify({
        "usuario": usuario,
        "nombre": nombre,
        "apellido": apellido,
        "rol": rol,
        "sucursal_id": sucursal_id,
        "sucursal_nombre": SUCURSALES.get(sucursal_id, "Desconocida"),
        "zona_asignada": zona_asignada,
        "asistencia_id": asistencia_id,
    })


@app.route("/api/logout", methods=["POST"])
def logout():
    datos = request.get_json() or {}
    asistencia_id = datos.get("asistencia_id")
    if not asistencia_id:
        return jsonify({"error": "Falta asistencia_id"}), 400

    from bson import ObjectId
    db.asistencia.update_one({"_id": ObjectId(asistencia_id)}, {"$set": {"hora_salida": ahora()}})
    return jsonify({"mensaje": "Salida registrada"})


# Tabla de asistencia del día para gerente/administrador.
# Incluye a TODOS los usuarios del sistema (aunque no hayan entrado hoy -> "Falta")
@app.route("/api/asistencia", methods=["GET"])
def obtener_asistencia():
    registros_hoy = {
        (r["usuario"]): r for r in db.asistencia.find({"fecha": hoy()})
    }

    resultado = []
    for u in db.usuarios.find():
        registro = registros_hoy.get(u["usuario"])

        if not registro:
            resultado.append({
                "usuario": u["usuario"],
                "nombre": "-",
                "apellido": "-",
                "rol": u["rol"],
                "sucursal_nombre": "-",
                "hora_entrada": "-",
                "hora_salida": "-",
                "estado": "Falta",
            })
            continue

        if registro["hora_entrada"] > HORA_LIMITE:
            estado = "Atrasado"
        elif registro.get("hora_salida"):
            estado = "Finalizó turno"
        else:
            estado = "Ya ingresó"

        resultado.append({
            "usuario": registro["usuario"],
            "nombre": registro["nombre"],
            "apellido": registro["apellido"],
            "rol": registro["rol"],
            "sucursal_nombre": SUCURSALES.get(registro["sucursal_id"], "-"),
            "hora_entrada": registro["hora_entrada"],
            "hora_salida": registro.get("hora_salida") or "-",
            "estado": estado,
        })

    return jsonify(resultado)


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
        {"$push": {"transacciones": transaccion}, "$inc": {"cantidad_disponible": cambio}},
    )
    if resultado.matched_count == 0:
        return jsonify({"error": "No existe inventario para esa sucursal/producto"}), 404

    return jsonify({"mensaje": "Movimiento registrado", "transaccion": transaccion}), 201


# ==========================================================
# TRANSACCIONES (aplanadas, para gerente)
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
# GANANCIAS POR SUCURSAL
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
                ingresos[inv["sucursal_id"]] = ingresos.get(inv["sucursal_id"], 0) + t["cantidad"] * producto["precio_venta"]

    resultado = [
        {"sucursal_id": sid, "sucursal_nombre": nombre, "ingresos_totales": ingresos.get(sid, 0)}
        for sid, nombre in SUCURSALES.items()
    ]
    return jsonify(resultado)


# ==========================================================
# VENTAS (rol cajero) - registra venta + comprobante + baja stock
# ==========================================================
@app.route("/api/ventas", methods=["POST"])
def registrar_venta():
    datos = request.get_json() or {}
    sucursal_id = datos.get("sucursal_id")
    sku_id = datos.get("sku_id")
    cantidad = datos.get("cantidad")
    comprobante = (datos.get("comprobante") or "").strip()
    cajero = datos.get("cajero", "")

    if not comprobante:
        return jsonify({"error": "El código de comprobante es obligatorio"}), 400
    try:
        sucursal_id, sku_id, cantidad = int(sucursal_id), int(sku_id), int(cantidad)
    except (TypeError, ValueError):
        return jsonify({"error": "sucursal_id, sku_id y cantidad deben ser números"}), 400
    if cantidad <= 0:
        return jsonify({"error": "cantidad debe ser mayor a 0"}), 400

    producto = db.productos.find_one({"sku_id": sku_id})
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    inv = db.inventario.find_one({"sucursal_id": sucursal_id, "sku_id": sku_id})
    if not inv:
        return jsonify({"error": "Ese producto no tiene inventario en esa sucursal"}), 404
    if inv["cantidad_disponible"] < cantidad:
        return jsonify({"error": f"Stock insuficiente (disponible: {inv['cantidad_disponible']})"}), 400

    monto_total = cantidad * producto["precio_venta"]
    transaccion = {
        "tipo": "salida",
        "cantidad": cantidad,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "motivo": f"Venta en caja - Comprobante {comprobante}",
    }

    db.inventario.update_one(
        {"sucursal_id": sucursal_id, "sku_id": sku_id},
        {"$push": {"transacciones": transaccion}, "$inc": {"cantidad_disponible": -cantidad}},
    )

    venta = {
        "sucursal_id": sucursal_id,
        "sucursal_nombre": SUCURSALES.get(sucursal_id, "Desconocida"),
        "sku_id": sku_id,
        "producto": producto["nombre"],
        "cantidad": cantidad,
        "precio_unitario": producto["precio_venta"],
        "monto_total": monto_total,
        "comprobante": comprobante,
        "cajero": cajero,
        "fecha": transaccion["fecha"],
    }
    db.ventas.insert_one(venta)

    return jsonify({"mensaje": "Venta registrada", "venta": limpiar(venta)}), 201


@app.route("/api/ventas", methods=["GET"])
def obtener_ventas():
    sucursal_id = request.args.get("sucursal_id", type=int)
    filtro = {"sucursal_id": sucursal_id} if sucursal_id else {}
    ventas = [limpiar(v) for v in db.ventas.find(filtro).sort("fecha", -1)]
    return jsonify(ventas)


# ==========================================================
# TAREAS DE REPOSICIÓN (rol inspector -> rol reponedor)
# ==========================================================
@app.route("/api/tareas", methods=["POST"])
def crear_tarea():
    datos = request.get_json() or {}
    sucursal_id = datos.get("sucursal_id")
    sku_id = datos.get("sku_id")
    creado_por = datos.get("creado_por", "")

    producto = db.productos.find_one({"sku_id": sku_id})
    tarea = {
        "sucursal_id": int(sucursal_id),
        "sucursal_nombre": SUCURSALES.get(int(sucursal_id), "Desconocida"),
        "sku_id": int(sku_id),
        "producto": producto["nombre"] if producto else f"SKU {sku_id}",
        "creado_por": creado_por,
        "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "atendida": False,
        "fecha_atencion": None,
    }
    db.tareas_reposicion.insert_one(tarea)
    return jsonify(limpiar(tarea)), 201


@app.route("/api/tareas", methods=["GET"])
def obtener_tareas():
    sucursal_id = request.args.get("sucursal_id", type=int)
    filtro = {"atendida": False}
    if sucursal_id:
        filtro["sucursal_id"] = sucursal_id
    tareas = [limpiar(t) for t in db.tareas_reposicion.find(filtro)]
    return jsonify(tareas)


@app.route("/api/tareas/<tarea_id>/completar", methods=["PATCH"])
def completar_tarea(tarea_id):
    from bson import ObjectId
    db.tareas_reposicion.update_one(
        {"_id": ObjectId(tarea_id)},
        {"$set": {"atendida": True, "fecha_atencion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}},
    )
    return jsonify({"mensaje": "Tarea marcada como completada"})


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
