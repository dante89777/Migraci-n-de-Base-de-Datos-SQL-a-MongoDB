from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # permite que index.html (abierto en el navegador) llame a esta API

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
    """Convierte el _id de Mongo (ObjectId) a texto para que se pueda mandar como JSON."""
    doc["_id"] = str(doc["_id"])
    return doc


@app.route("/api/productos", methods=["GET"])
def obtener_productos():
    productos = [limpiar(p) for p in db.productos.find()]
    return jsonify(productos)


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


@app.route("/api/inventario", methods=["GET"])
def obtener_inventario():
    inventarios = []
    for inv in db.inventario.find():
        inv = limpiar(inv)
        inv["sucursal_nombre"] = SUCURSALES.get(inv.get("sucursal_id"), "Desconocida")
        inventarios.append(inv)
    return jsonify(inventarios)


@app.route("/api/estadisticas", methods=["GET"])
def obtener_estadisticas():
    total_productos = db.productos.count_documents({})
    total_inventarios = db.inventario.count_documents({})

    total_transacciones = 0
    for inv in db.inventario.find():
        total_transacciones += len(inv.get("transacciones", []))

    return jsonify({
        "productos": total_productos,
        "inventarios": total_inventarios,
        "transacciones": total_transacciones,
        "sucursales": len(SUCURSALES),
    })


if __name__ == "__main__":
    print("API corriendo en http://localhost:5000")
    app.run(debug=True, port=5000)
