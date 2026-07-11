const API_URL = "http://localhost:5000/api";

let productos = [];
let inventario = [];

// ==============================
// READ: traer datos desde la API
// ==============================
async function cargarProductos() {
  try {
    const respuesta = await fetch(`${API_URL}/productos`);
    productos = await respuesta.json();
    mostrarProductos();
  } catch (error) {
    mostrarErrorConexion();
    console.error("Error cargando productos:", error);
  }
}

async function cargarInventario() {
  try {
    const respuesta = await fetch(`${API_URL}/inventario`);
    inventario = await respuesta.json();
    mostrarInventario();
  } catch (error) {
    console.error("Error cargando inventario:", error);
  }
}

async function cargarEstadisticas() {
  try {
    const respuesta = await fetch(`${API_URL}/estadisticas`);
    const stats = await respuesta.json();
    document.getElementById("statProductos").textContent = stats.productos;
    document.getElementById("statInventarios").textContent = stats.inventarios;
    document.getElementById("statTransacciones").textContent = stats.transacciones;
  } catch (error) {
    console.error("Error cargando estadísticas:", error);
  }
}

function mostrarErrorConexion() {
  const tabla = document.getElementById("tablaProductos");
  tabla.innerHTML = `
    <tr>
      <td colspan="5">
        No se pudo conectar con la API (${API_URL}).
        Verifica que <code>api.py</code> esté corriendo.
      </td>
    </tr>`;
}

// ==============================
// Render: tabla de productos
// ==============================
function mostrarProductos() {
  const tabla = document.getElementById("tablaProductos");
  tabla.innerHTML = "";

  productos.forEach((producto) => {
    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${producto.sku_id}</td>
      <td>${producto.nombre}</td>
      <td>${producto.categoria}</td>
      <td>${producto.stock_minimo ?? "-"}&ndash;${producto.stock_maximo ?? "-"}</td>
      <td>
        <button class="btn-eliminar" onclick="eliminarProducto(${producto.sku_id})">Eliminar</button>
      </td>
    `;
    tabla.appendChild(fila);
  });
}

// ==============================
// Render: tabla de inventario
// ==============================
function mostrarInventario() {
  const tabla = document.getElementById("tablaInventario");
  tabla.innerHTML = "";

  inventario.forEach((item) => {
    const producto = productos.find((p) => p.sku_id === item.sku_id);
    const nombreProducto = producto ? producto.nombre : `SKU ${item.sku_id}`;
    const stockBajo = producto && item.cantidad_disponible < producto.stock_minimo;

    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${item.sucursal_nombre}</td>
      <td>${nombreProducto}</td>
      <td class="${stockBajo ? "stock-bajo" : ""}">${item.cantidad_disponible}</td>
      <td>${item.cantidad_reservada}</td>
      <td>${item.cantidad_en_transito}</td>
      <td>${item.fecha_ultimo_recuento}</td>
    `;
    tabla.appendChild(fila);
  });
}

// ==============================
// CREATE: agregar producto (POST a la API)
// ==============================
async function agregarProducto(evento) {
  evento.preventDefault();

  const nombre = document.getElementById("nombre").value.trim();
  const categoria = document.getElementById("categoria").value.trim();
  const stock = document.getElementById("stock").value.trim();

  if (nombre === "" || categoria === "" || stock === "") {
    alert("Complete todos los campos");
    return;
  }

  try {
    await fetch(`${API_URL}/productos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nombre,
        categoria,
        stock_minimo: Number(stock),
        stock_maximo: Number(stock) * 4,
      }),
    });

    document.getElementById("formProducto").reset();
    await cargarProductos();
    await cargarEstadisticas();
  } catch (error) {
    alert("No se pudo agregar el producto. Revisa que la API esté corriendo.");
    console.error(error);
  }
}

// ==============================
// DELETE: eliminar producto (DELETE a la API)
// ==============================
async function eliminarProducto(sku_id) {
  try {
    await fetch(`${API_URL}/productos/${sku_id}`, { method: "DELETE" });
    await cargarProductos();
    await cargarEstadisticas();
  } catch (error) {
    alert("No se pudo eliminar el producto.");
    console.error(error);
  }
}

// ==============================
// Búsqueda en vivo (sobre lo ya cargado, sin llamar la API de nuevo)
// ==============================
function buscarProducto() {
  const texto = document.getElementById("busqueda").value.toLowerCase();
  const filas = document.querySelectorAll("#tablaProductos tr");

  filas.forEach((fila) => {
    const contenido = fila.textContent.toLowerCase();
    fila.style.display = contenido.includes(texto) ? "" : "none";
  });
}

// ==============================
// Inicialización
// ==============================
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("fecha").textContent = new Date().toLocaleString("es-CL");
  document.getElementById("formProducto").addEventListener("submit", agregarProducto);

  cargarProductos().then(() => {
    cargarInventario();
  });
  cargarEstadisticas();
});
