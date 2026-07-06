from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["InventoryOptimizer"]

print("=== TRANSACCIONES ENTRADA ===")

for inventario in db.inventario.find(
    {
        "transacciones": {
            "$elemMatch": {
                "tipo": "entrada"
            }
        }
    }
):

    print(
        f"Inventario: {inventario['inventario_id']}"
    )

    print(
        f"Cantidad Transacciones: {len(inventario['transacciones'])}"
    )