from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["InventoryOptimizer"]

db.productos.delete_many({})

print("Productos eliminados")