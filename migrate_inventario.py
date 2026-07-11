from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["InventoryOptimizer"]

productos = [
    {"sku_id": 1,  "codigo_barra": "7501234567890", "nombre": "Leche Entera 1L",
     "categoria": "lácteos", "proveedor_id": 10, "precio_costo": 800, "precio_venta": 1290,
     "unidad_medida": "unidad", "tiempo_reorden_dias": 3, "stock_minimo": 20, "stock_maximo": 100},

    {"sku_id": 2,  "codigo_barra": "7501234567891", "nombre": "Yogur Natural 500g",
     "categoria": "lácteos", "proveedor_id": 10, "precio_costo": 950, "precio_venta": 1790,
     "unidad_medida": "unidad", "tiempo_reorden_dias": 3, "stock_minimo": 15, "stock_maximo": 80},

    {"sku_id": 3,  "codigo_barra": "7501234567892", "nombre": "Queso Fresco 500g",
     "categoria": "lácteos", "proveedor_id": 11, "precio_costo": 3500, "precio_venta": 5990,
     "unidad_medida": "unidad", "tiempo_reorden_dias": 5, "stock_minimo": 10, "stock_maximo": 40},

    {"sku_id": 4,  "codigo_barra": "7501234567893", "nombre": "Pan Integral 700g",
     "categoria": "panadería", "proveedor_id": 12, "precio_costo": 1200, "precio_venta": 2490,
     "unidad_medida": "unidad", "tiempo_reorden_dias": 1, "stock_minimo": 30, "stock_maximo": 150},

    {"sku_id": 5,  "codigo_barra": "7501234567894", "nombre": "Cereal Integral 500g",
     "categoria": "desayuno", "proveedor_id": 13, "precio_costo": 2000, "precio_venta": 3990,
     "unidad_medida": "unidad", "tiempo_reorden_dias": 7, "stock_minimo": 15, "stock_maximo": 60},

    {"sku_id": 6,  "codigo_barra": "7501234567895", "nombre": "Aceite Vegetal 1L",
     "categoria": "condimentos", "proveedor_id": 14, "precio_costo": 2500, "precio_venta": 4290,
     "unidad_medida": "unidad", "tiempo_reorden_dias": 10, "stock_minimo": 12, "stock_maximo": 50},

    {"sku_id": 7,  "codigo_barra": "7501234567896", "nombre": "Café Molido 500g",
     "categoria": "bebidas", "proveedor_id": 15, "precio_costo": 4000, "precio_venta": 7990,
     "unidad_medida": "unidad", "tiempo_reorden_dias": 7, "stock_minimo": 8, "stock_maximo": 40},

    {"sku_id": 8,  "codigo_barra": "7501234567897", "nombre": "Chocolate 150g",
     "categoria": "golosinas", "proveedor_id": 16, "precio_costo": 1500, "precio_venta": 2990,
     "unidad_medida": "unidad", "tiempo_reorden_dias": 14, "stock_minimo": 20, "stock_maximo": 100},

    {"sku_id": 9,  "codigo_barra": "7501234567898", "nombre": "Galletas Integrales 300g",
     "categoria": "golosinas", "proveedor_id": 16, "precio_costo": 1200, "precio_venta": 2290,
     "unidad_medida": "unidad", "tiempo_reorden_dias": 7, "stock_minimo": 25, "stock_maximo": 120},

    {"sku_id": 10, "codigo_barra": "7501234567899", "nombre": "Mermelada Fresa 340g",
     "categoria": "conservas", "proveedor_id": 17, "precio_costo": 1800, "precio_venta": 3290,
     "unidad_medida": "unidad", "tiempo_reorden_dias": 14, "stock_minimo": 10, "stock_maximo": 50},
]

db.productos.delete_many({})
db.productos.insert_many(productos)

print(f"{len(productos)} productos cargados correctamente")
