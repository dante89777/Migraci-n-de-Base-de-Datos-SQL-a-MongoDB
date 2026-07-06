from pymongo import MongoClient
from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["InventoryOptimizer"]

productos = list(db.productos.find())
inventarios = list(db.inventario.find())

print("Productos encontrados:", len(productos))
print("Inventarios encontrados:", len(inventarios))

ids_productos = [p["sku_id"] for p in productos]

for inv in inventarios:

    if inv["sku_id"] in ids_productos:
        print(f"SKU {inv['sku_id']} correcto")
    else:
        print(f"SKU {inv['sku_id']} no existe")