from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["InventoryOptimizer"]

inventarios = [
    {"inventario_id": 1, "sucursal_id": 1, "sku_id": 1, "cantidad_disponible": 45,
     "cantidad_reservada": 5, "cantidad_en_transito": 20, "fecha_ultimo_recuento": "2024-06-10",
     "transacciones": [
         {"tipo": "entrada", "cantidad": 50, "fecha": "2024-06-08 09:00:00", "motivo": "Compra a proveedor"},
         {"tipo": "salida", "cantidad": 5, "fecha": "2024-06-09 14:30:00", "motivo": "Venta en caja"},
     ]},
    {"inventario_id": 2, "sucursal_id": 1, "sku_id": 2, "cantidad_disponible": 35,
     "cantidad_reservada": 3, "cantidad_en_transito": 15, "fecha_ultimo_recuento": "2024-06-10",
     "transacciones": [
         {"tipo": "entrada", "cantidad": 40, "fecha": "2024-06-08 10:15:00", "motivo": "Compra a proveedor"},
         {"tipo": "salida", "cantidad": 5, "fecha": "2024-06-10 11:20:00", "motivo": "Venta en caja"},
     ]},
    {"inventario_id": 3, "sucursal_id": 1, "sku_id": 3, "cantidad_disponible": 18,
     "cantidad_reservada": 2, "cantidad_en_transito": 10, "fecha_ultimo_recuento": "2024-06-10",
     "transacciones": [
         {"tipo": "entrada", "cantidad": 25, "fecha": "2024-06-07 08:45:00", "motivo": "Compra a proveedor"},
         {"tipo": "salida", "cantidad": 7, "fecha": "2024-06-10 16:00:00", "motivo": "Venta en caja"},
     ]},
    {"inventario_id": 4, "sucursal_id": 1, "sku_id": 4, "cantidad_disponible": 85,
     "cantidad_reservada": 10, "cantidad_en_transito": 30, "fecha_ultimo_recuento": "2024-06-10",
     "transacciones": [
         {"tipo": "entrada", "cantidad": 100, "fecha": "2024-06-06 07:30:00", "motivo": "Compra a proveedor"},
         {"tipo": "salida", "cantidad": 15, "fecha": "2024-06-10 18:45:00", "motivo": "Venta en caja"},
     ]},
    {"inventario_id": 5, "sucursal_id": 1, "sku_id": 5, "cantidad_disponible": 28,
     "cantidad_reservada": 4, "cantidad_en_transito": 0, "fecha_ultimo_recuento": "2024-06-10",
     "transacciones": [
         {"tipo": "entrada", "cantidad": 30, "fecha": "2024-06-01 09:00:00", "motivo": "Compra a proveedor"},
         {"tipo": "salida", "cantidad": 2, "fecha": "2024-06-10 13:15:00", "motivo": "Venta en caja"},
     ]},
    {"inventario_id": 6, "sucursal_id": 2, "sku_id": 1, "cantidad_disponible": 52,
     "cantidad_reservada": 8, "cantidad_en_transito": 25, "fecha_ultimo_recuento": "2024-06-10",
     "transacciones": [
         {"tipo": "entrada", "cantidad": 60, "fecha": "2024-06-08 09:30:00", "motivo": "Compra a proveedor"},
         {"tipo": "salida", "cantidad": 8, "fecha": "2024-06-10 15:20:00", "motivo": "Venta en caja"},
     ]},
    {"inventario_id": 7, "sucursal_id": 2, "sku_id": 2, "cantidad_disponible": 22,
     "cantidad_reservada": 2, "cantidad_en_transito": 12, "fecha_ultimo_recuento": "2024-06-10",
     "transacciones": []},
    {"inventario_id": 8, "sucursal_id": 2, "sku_id": 3, "cantidad_disponible": 5,
     "cantidad_reservada": 0, "cantidad_en_transito": 5, "fecha_ultimo_recuento": "2024-06-10",
     "transacciones": [
         {"tipo": "entrada", "cantidad": 10, "fecha": "2024-06-09 10:00:00", "motivo": "Compra a proveedor"},
         {"tipo": "salida", "cantidad": 5, "fecha": "2024-06-10 14:00:00", "motivo": "Venta en caja"},
     ]},
    {"inventario_id": 9, "sucursal_id": 2, "sku_id": 4, "cantidad_disponible": 95,
     "cantidad_reservada": 15, "cantidad_en_transito": 40, "fecha_ultimo_recuento": "2024-06-10",
     "transacciones": []},
    {"inventario_id": 10, "sucursal_id": 3, "sku_id": 1, "cantidad_disponible": 38,
     "cantidad_reservada": 6, "cantidad_en_transito": 18, "fecha_ultimo_recuento": "2024-06-10",
     "transacciones": [
         {"tipo": "entrada", "cantidad": 45, "fecha": "2024-06-08 08:00:00", "motivo": "Compra a proveedor"},
         {"tipo": "salida", "cantidad": 7, "fecha": "2024-06-10 12:30:00", "motivo": "Venta en caja"},
     ]},
    {"inventario_id": 11, "sucursal_id": 3, "sku_id": 5, "cantidad_disponible": 0,
     "cantidad_reservada": 0, "cantidad_en_transito": 0, "fecha_ultimo_recuento": "2024-06-08",
     "transacciones": [
         {"tipo": "entrada", "cantidad": 0, "fecha": "2024-06-08 08:00:00", "motivo": "Pedido pendiente"},
         {"tipo": "ajuste", "cantidad": 0, "fecha": "2024-06-08 15:00:00", "motivo": "Stock no recibido"},
     ]},
    {"inventario_id": 12, "sucursal_id": 3, "sku_id": 6, "cantidad_disponible": 42,
     "cantidad_reservada": 5, "cantidad_en_transito": 20, "fecha_ultimo_recuento": "2024-06-10",
     "transacciones": []},
    {"inventario_id": 13, "sucursal_id": 4, "sku_id": 1, "cantidad_disponible": 28,
     "cantidad_reservada": 4, "cantidad_en_transito": 12, "fecha_ultimo_recuento": "2024-06-09",
     "transacciones": [
         {"tipo": "entrada", "cantidad": 35, "fecha": "2024-06-08 07:45:00", "motivo": "Compra a proveedor"},
         {"tipo": "salida", "cantidad": 7, "fecha": "2024-06-09 16:45:00", "motivo": "Venta en caja"},
     ]},
    {"inventario_id": 14, "sucursal_id": 4, "sku_id": 7, "cantidad_disponible": 15,
     "cantidad_reservada": 2, "cantidad_en_transito": 8, "fecha_ultimo_recuento": "2024-06-10",
     "transacciones": []},
    {"inventario_id": 15, "sucursal_id": 5, "sku_id": 8, "cantidad_disponible": 0,
     "cantidad_reservada": 0, "cantidad_en_transito": 0, "fecha_ultimo_recuento": "2024-06-07",
     "transacciones": []},
]

db.inventario.delete_many({})
db.inventario.insert_many(inventarios)

print(f"{len(inventarios)} inventarios cargados correctamente")
