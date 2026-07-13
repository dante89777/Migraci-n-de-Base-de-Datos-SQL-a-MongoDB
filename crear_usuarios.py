from pymongo import MongoClient
from werkzeug.security import generate_password_hash

cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["InventoryOptimizer"]

# La contraseña valida el ROL. El nombre, apellido y sucursal los escribe
# la persona real al momento de entrar (así una misma cuenta la puede usar
# cualquier trabajador de ese rol, y queda registrado quién fue).
usuarios = [
    {"usuario": "admin",       "password_hash": generate_password_hash("admin123"),   "rol": "administrador"},
    {"usuario": "gerente1",    "password_hash": generate_password_hash("gerente123"), "rol": "gerente"},
    {"usuario": "reponedor1",  "password_hash": generate_password_hash("repo123"),    "rol": "reponedor"},
    {"usuario": "reponedor2",  "password_hash": generate_password_hash("repo456"),    "rol": "reponedor"},
    {"usuario": "cajero1",     "password_hash": generate_password_hash("caja123"),    "rol": "cajero"},
    {"usuario": "seguridad1",  "password_hash": generate_password_hash("seg123"),     "rol": "seguridad"},
    {"usuario": "inspector1",  "password_hash": generate_password_hash("insp123"),    "rol": "inspector"},
]

db.usuarios.delete_many({})
db.usuarios.insert_many(usuarios)

claves = {"admin": "admin123", "gerente1": "gerente123", "reponedor1": "repo123",
          "reponedor2": "repo456", "cajero1": "caja123", "seguridad1": "seg123",
          "inspector1": "insp123"}

print(f"{len(usuarios)} usuarios creados correctamente\n")
print("Credenciales para probar (todos piden además nombre, apellido y sucursal al entrar):")
for u in usuarios:
    print(f"  usuario: {u['usuario']:<12} password: {claves[u['usuario']]:<10} rol: {u['rol']}")
