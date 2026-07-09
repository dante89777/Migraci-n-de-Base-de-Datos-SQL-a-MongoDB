let productos = [
  { sku_id: 1,  nombre: "Leche Entera 1L",         categoria: "lácteos",     stock_min: 20, stock_max: 100 },
  { sku_id: 2,  nombre: "Yogur Natural 500g",       categoria: "lácteos",     stock_min: 15, stock_max: 80 },
  { sku_id: 3,  nombre: "Queso Fresco 500g",        categoria: "lácteos",     stock_min: 10, stock_max: 40 },
  { sku_id: 4,  nombre: "Pan Integral 700g",        categoria: "panadería",   stock_min: 30, stock_max: 150 },
  { sku_id: 5,  nombre: "Cereal Integral 500g",     categoria: "desayuno",    stock_min: 15, stock_max: 60 },
  { sku_id: 6,  nombre: "Aceite Vegetal 1L",        categoria: "condimentos", stock_min: 12, stock_max: 50 },
  { sku_id: 7,  nombre: "Café Molido 500g",         categoria: "bebidas",     stock_min: 8,  stock_max: 40 },
  { sku_id: 8,  nombre: "Chocolate 150g",           categoria: "golosinas",   stock_min: 20, stock_max: 100 },
  { sku_id: 9,  nombre: "Galletas Integrales 300g", categoria: "golosinas",   stock_min: 25, stock_max: 120 },
  { sku_id: 10, nombre: "Mermelada Fresa 340g",     categoria: "conservas",   stock_min: 10, stock_max: 50 },
];

const sucursales = {
  1: "Sucursal Centro",
  2: "Sucursal Sur",
  3: "Sucursal Norte",
  4: "Sucursal Valparaíso",
  5: "Sucursal Concepción",
};

let inventario = [
  { sucursal_id: 1, sku_id: 1,  disponible: 45, reservado: 5,  transito: 20, recuento: "2024-06-10" },
  { sucursal_id: 1, sku_id: 2,  disponible: 35, reservado: 3,  transito: 15, recuento: "2024-06-10" },
  { sucursal_id: 1, sku_id: 3,  disponible: 18, reservado: 2,  transito: 10, recuento: "2024-06-10" },
  { sucursal_id: 1, sku_id: 4,  disponible: 85, reservado: 10, transito: 30, recuento: "2024-06-10" },
  { sucursal_id: 1, sku_id: 5,  disponible: 28, reservado: 4,  transito: 0,  recuento: "2024-06-10" },
  { sucursal_id: 2, sku_id: 1,  disponible: 52, reservado: 8,  transito: 25, recuento: "2024-06-10" },
  { sucursal_id: 2, sku_id: 2,  disponible: 22, reservado: 2,  transito: 12, recuento: "2024-06-10" },
  { sucursal_id: 2, sku_id: 3,  disponible: 5,  reservado: 0,  transito: 5,  recuento: "2024-06-10" },
  { sucursal_id: 2, sku_id: 4,  disponible: 95, reservado: 15, transito: 40, recuento: "2024-06-10" },
  { sucursal_id: 3, sku_id: 1,  disponible: 38, reservado: 6,  transito: 18, recuento: "2024-06-10" },
  { sucursal_id: 3, sku_id: 5,  disponible: 0,  reservado: 0,  transito: 0,  recuento: "2024-06-08" },
  { sucursal_id: 3, sku_id: 6,  disponible: 42, reservado: 5,  transito: 20, recuento: "2024-06-10" },
  { sucursal_id: 4, sku_id: 1,  disponible: 28, reservado: 4,  transito: 12, recuento: "2024-06-09" },
  { sucursal_id: 4, sku_id: 7,  disponible: 15, reservado: 2,  transito: 8,  recuento: "2024-06-10" },
  { sucursal_id: 5, sku_id: 8,  disponible: 0,  reservado: 0,  transito: 0,  recuento: "2024-06-07" },
];

const TOTAL_TRANSACCIONES = 20; // según CASO_10_InventoryOptimizer_datos_legacy.sql

function mostrarProductos() {
  const tabla = document.getElementById("tablaProductos");
  tabla.innerHTML = "";

  productos.forEach((producto) => {
    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${producto.sku_id}</td>
      <td>${producto.nombre}</td>
      <td>${producto.categoria}</td>
      <td>${producto.stock_min}&ndash;${producto.stock_max}</td>
      <td>
        <button class="btn-eliminar" onclick="eliminarProducto(${producto.sku_id})">Eliminar</button>
      </td>
    `;
    tabla.appendChild(fila);
  });

  actualizarEstadisticas();
}

function mostrarInventario() {
  const tabla = document.getElementById("tablaInventario");
  tabla.innerHTML = "";

  inventario.forEach((item) => {
    const producto = productos.find((p) => p.sku_id === item.sku_id);
    const nombreProducto = producto ? producto.nombre : `SKU ${item.sku_id}`;
    const stockBajo = producto && item.disponible < producto.stock_min;

    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${sucursales[item.sucursal_id] || item.sucursal_id}</td>
      <td>${nombreProducto}</td>
      <td class="${stockBajo ? "stock-bajo" : ""}">${item.disponible}</td>
      <td>${item.reservado}</td>
      <td>${item.transito}</td>
      <td>${item.recuento}</td>
    `;
    tabla.appendChild(fila);
  });
}

function agregarProducto(evento) {
  evento.preventDefault();

  const nombre = document.getElementById("nombre").value.trim();
  const categoria = document.getElementById("categoria").value.trim();
  const stock = document.getElementById("stock").value.trim();

  if (nombre === "" || categoria === "" || stock === "") {
    alert("Complete todos los campos");
    return;
  }

  const nuevoId = productos.length
    ? Math.max(...productos.map((p) => p.sku_id)) + 1
    : 1;

  productos.push({
    sku_id: nuevoId,
    nombre,
    categoria,
    stock_min: Number(stock),
    stock_max: Number(stock) * 4,
  });

  mostrarProductos();
  document.getElementById("formProducto").reset();
}

function eliminarProducto(sku_id) {
  productos = productos.filter((p) => p.sku_id !== sku_id);
  mostrarProductos();
}

function buscarProducto() {
  const texto = document.getElementById("busqueda").value.toLowerCase();
  const filas = document.querySelectorAll("#tablaProductos tr");

  filas.forEach((fila) => {
    const contenido = fila.textContent.toLowerCase();
    fila.style.display = contenido.includes(texto) ? "" : "none";
  });
}


function actualizarEstadisticas() {
  document.getElementById("statProductos").textContent = productos.length;
  document.getElementById("statInventarios").textContent = inventario.length;
  document.getElementById("statTransacciones").textContent = TOTAL_TRANSACCIONES;
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("fecha").textContent = new Date().toLocaleString("es-CL");
  document.getElementById("formProducto").addEventListener("submit", agregarProducto);
  mostrarProductos();
  mostrarInventario();
});