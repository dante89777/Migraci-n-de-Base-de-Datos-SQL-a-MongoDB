from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017/")

db = cliente["InventoryOptimizer"]

db.productos.insert_one({
    "sku_id": 1,
    "nombre": "Leche Entera 1L",
    "categoria": "lácteos",
    "precio_costo": 800,
    "precio_venta": 1290
})

print("Producto insertado")