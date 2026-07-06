from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017/")

db = cliente["InventoryOptimizer"]

productos = [
    {
        "sku_id": 1,
        "nombre": "Leche Entera 1L",
        "categoria": "lácteos",
        "precio_costo": 800,
        "precio_venta": 1290
    },
    {
        "sku_id": 2,
        "nombre": "Yogur Natural 500g",
        "categoria": "lácteos",
        "precio_costo": 950,
        "precio_venta": 1790
    },
    {
        "sku_id": 3,
        "nombre": "Queso Fresco 500g",
        "categoria": "lácteos",
        "precio_costo": 3500,
        "precio_venta": 5990
    },
    {
        "sku_id":1,
        "nombre":"Leche Entera 1L",
        "categoria":"lácteos",
        "precio_costo":800,
        "precio_venta":1290
    },
    {
        "sku_id":2,
        "nombre":"Yogur Natural 500g",
        "categoria":"lácteos",
        "precio_costo":950,
        "precio_venta":1790
    },
    {
        "sku_id":3,
        "nombre":"Queso Fresco 500g",
        "categoria":"lácteos",
        "precio_costo":3500,
        "precio_venta":5990
    },
    {
        "sku_id":4,
        "nombre":"Pan Integral 700g",
        "categoria":"panadería",
        "precio_costo":1200,
        "precio_venta":2490
    },
    {
        "sku_id":5,
        "nombre":"Cereal Integral 500g",
        "categoria":"desayuno",
        "precio_costo":2000,
        "precio_venta":3990
    },
    {
        "sku_id":6,
        "nombre":"Aceite Vegetal 1L",
        "categoria":"condimentos",
        "precio_costo":2500,
        "precio_venta":4290
    },
    {
        "sku_id":7,
        "nombre":"Café Molido 500g",
        "categoria":"bebidas",
        "precio_costo":4000,
        "precio_venta":7990
    },
    {
        "sku_id":8,
        "nombre":"Chocolate 150g",
        "categoria":"golosinas",
        "precio_costo":1500,
        "precio_venta":2990
    },
    {
        "sku_id":9,
        "nombre":"Galletas Integrales 300g",
        "categoria":"golosinas",
        "precio_costo":1200,
        "precio_venta":2290
    },
    {
        "sku_id":10,
        "nombre":"Mermelada Fresa 340g",
        "categoria":"conservas",
        "precio_costo":1800,
        "precio_venta":3290
    }
]

db.productos.delete_many({})
db.productos.insert_many(productos)

print("Productos cargados correctamente")

