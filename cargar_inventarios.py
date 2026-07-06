from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["InventoryOptimizer"]

inventarios = [

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
},

{
"inventario_id":4,
"sucursal_id":1,
"sku_id":4,
"cantidad_disponible":85,
"transacciones":[
{"tipo":"entrada","cantidad":100},
{"tipo":"salida","cantidad":15}
]
},

{
"inventario_id":5,
"sucursal_id":1,
"sku_id":5,
"cantidad_disponible":28,
"transacciones":[
{"tipo":"entrada","cantidad":30},
{"tipo":"salida","cantidad":2}
]
},

{
"inventario_id":6,
"sucursal_id":2,
"sku_id":1,
"cantidad_disponible":52,
"transacciones":[
{"tipo":"entrada","cantidad":60},
{"tipo":"salida","cantidad":8}
]
},

{
"inventario_id":7,
"sucursal_id":2,
"sku_id":2,
"cantidad_disponible":22,
"transacciones":[]
},

{
"inventario_id":8,
"sucursal_id":2,
"sku_id":3,
"cantidad_disponible":5,
"transacciones":[
{"tipo":"entrada","cantidad":10},
{"tipo":"salida","cantidad":5}
]
},

{
"inventario_id":9,
"sucursal_id":2,
"sku_id":4,
"cantidad_disponible":95,
"transacciones":[]
},

{
"inventario_id":10,
"sucursal_id":3,
"sku_id":1,
"cantidad_disponible":38,
"transacciones":[
{"tipo":"entrada","cantidad":45},
{"tipo":"salida","cantidad":7}
]
},

{
"inventario_id":11,
"sucursal_id":3,
"sku_id":5,
"cantidad_disponible":0,
"transacciones":[
{"tipo":"entrada","cantidad":0},
{"tipo":"ajuste","cantidad":0}
]
},

{
"inventario_id":12,
"sucursal_id":3,
"sku_id":6,
"cantidad_disponible":42,
"transacciones":[]
},

{
"inventario_id":13,
"sucursal_id":4,
"sku_id":1,
"cantidad_disponible":28,
"transacciones":[
{"tipo":"entrada","cantidad":35},
{"tipo":"salida","cantidad":7}
]
},

{
"inventario_id":14,
"sucursal_id":4,
"sku_id":7,
"cantidad_disponible":15,
"transacciones":[]
},

{
"inventario_id":15,
"sucursal_id":5,
"sku_id":8,
"cantidad_disponible":0,
"transacciones":[]
}

]

db.inventario.delete_many({})
db.inventario.insert_many(inventarios)

print("15 inventarios cargados")