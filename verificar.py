from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017/")

db = cliente["InventoryOptimizer"]

for producto in db.productos.find():
    print(producto)