from pymongo import MongoClient

try:
    cliente = MongoClient("mongodb://localhost:27017/")
    cliente.admin.command("ping")

    print("MongoDB conectado correctamente")

except Exception as e:
    print("Error:", e)

print("Fin del programa")