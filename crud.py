from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["InventoryOptimizer"]

# CREATE - Agregar transacción

db.inventario.update_one(
    {"inventario_id": 1},
    {
        "$push": {
            "transacciones": {
                "tipo": "salida",
                "cantidad": 3,
                "fecha": "2024-06-11",
                "motivo": "Venta"
            }
        }
    }
)

print("Transacción agregada")

# UPDATE - Actualizar stock

db.inventario.update_one(
    {"inventario_id": 1},
    {
        "$set": {
            "cantidad_disponible": 42
        }
    }
)

print("Stock actualizado")

# DELETE - Eliminar ajuste

db.inventario.update_one(
    {},
    {
        "$pull": {
            "transacciones": {
                "tipo": "ajuste"
            }
        }
    }
)

print("Ajustes eliminados")