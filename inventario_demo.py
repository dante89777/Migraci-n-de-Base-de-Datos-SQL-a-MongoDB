from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["InventoryOptimizer"]

inventario = [
{
"inventario_id": 1,
"sucursal_id": 1,
"sku_id": 1,
"cantidad_disponible": 45,
"cantidad_reservada": 5,
"cantidad_en_transito": 20,
"transacciones": [
{
"tipo": "entrada",
"cantidad": 50
},
{
"tipo": "salida",
"cantidad": 5
}
]
},
{
"inventario_id": 2,
"sucursal_id": 1,
"sku_id": 2,
"cantidad_disponible": 35,
"cantidad_reservada": 3,
"cantidad_en_transito": 15,
"transacciones": [
{
"tipo": "entrada",
"cantidad": 40
},
{
"tipo": "salida",
"cantidad": 5
}
]
},
{
"inventario_id":1,
"sucursal_id":1,
"sku_id":1,
"cantidad_disponible":45,
"transacciones":[
{"tipo":"entrada","cantidad":50},
{"tipo":"salida","cantidad":5}
]
},

{
"inventario_id":2,
"sucursal_id":1,
"sku_id":2,
"cantidad_disponible":35,
"transacciones":[
{"tipo":"entrada","cantidad":40},
{"tipo":"salida","cantidad":5}
]
},
{
"inventario_id":3,
"sucursal_id":1,
"sku_id":3,
"cantidad_disponible":18,
"transacciones":[
{"tipo":"entrada","cantidad":25},
{"tipo":"salida","cantidad":7}

]
}
]


db.inventario.delete_many({})
db.inventario.insert_many(inventario)

print("Inventario cargado correctamente")