from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["InventoryOptimizer"]

print("\n=== PRODUCTOS LACTEOS ===")

for p in db.productos.find(
    {"categoria": "lácteos"}
):
    print(p["nombre"])

print("\n=== STOCK MAYOR A 30 ===")

for i in db.inventario.find(
    {"cantidad_disponible": {"$gt": 30}}
):
    print(
        f"Inventario {i['inventario_id']} - Stock: {i['cantidad_disponible']}"
    )

print("\n=== SUCURSAL 1 ===")

for i in db.inventario.find(
    {"sucursal_id": 1}
):
    print(i)