from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["InventoryOptimizer"]

for p in db.productos.find():
    print(p)

