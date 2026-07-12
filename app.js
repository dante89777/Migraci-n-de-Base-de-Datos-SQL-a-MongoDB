const API_URL = "http://localhost:5000/api";

let currentUser = null; // se pierde al recargar la página (hay que loguearse de nuevo)
let productos = [];
let inventario = [];

// Mapea la categoría de cada producto a una zona del mapa de la sucursal
const CATEGORIA_A_ZONA = {
  "lácteos": "zona-lacteos",
  "panadería": "zona-panaderia",
  "condimentos": "zona-condimentos",
  "bebidas": "zona-bebidas",
  "golosinas": "zona-golosinas",
  "conservas": "zona-conservas",
  "desayuno": "zona-congelados",
};

// ==============================
// LOGIN / LOGOUT
// ==============================
document.getElementById("formLogin").addEventListener("submit", async (evento) => {
  evento.preventDefault();

  const usuario = document.getElementById("loginUsuario").value.trim();
  const password = document.getElementById("loginPassword").value;
  const errorEl = document.getElementById("loginError");
  errorEl.textContent = "";

  try {
    const respuesta = await fetch(`${API_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ usuario, password }),
    });

    if (!respuesta.ok) {
      const datos = await respuesta.json();
      errorEl.textContent = datos.error || "No se pudo iniciar sesión";
      return;
    }

    currentUser = await respuesta.json();
    iniciarApp();
  } catch (error) {
    errorEl.textContent = "No se pudo conectar con la API. ¿Está corriendo api.py?";
    console.error(error);
  }
});

document.getElementById("btnLogout").addEventListener("click", () => {
  currentUser = null;
  document.getElementById("appRoot").style.display = "none";
  document.getElementById("pantallaLogin").style.display = "flex";
  document.getElementById("loginUsuario").value = "";
  document.getElementById("loginPassword").value = "";
});

// ==============================
// Arranque de la app tras login
// ==============================
function iniciarApp() {
  document.getElementById("pantallaLogin").style.display = "none";
  document.getElementById("appRoot").style.display = "block";
  document.getElementById("infoUsuario").textContent =
    `${currentUser.nombre} — rol: ${currentUser.rol}`;

  aplicarPermisosPorRol(currentUser.rol);

  if (currentUser.rol === "gerente" || currentUser.rol === "administrador") {
    cargarEstadisticas();
    cargarGanancias();
    cargarTransacciones();
  }

  if (currentUser.rol === "administrador") {
    document.getElementById("formProducto").addEventListener("submit", agregarProducto);
  }

  // productos e inventario se usan en varias vistas, se cargan siempre
  cargarProductos().then(() => {
    cargarInventario().then(() => {
      if (currentUser.rol === "reponedor") {
        dibujarMapa();
        mostrarAlertasReponedor();
      }
    });
  });
}

// Muestra/oculta secciones según el atributo data-roles de cada una
function aplicarPermisosPorRol(rol) {
  document.querySelectorAll("[data-roles]").forEach((el) => {
    const permitidos = el.dataset.roles.split(",");
    el.style.display = permitidos.includes(rol) ? "" : "none";
  });
}

// ==============================
// Carga de datos desde la API
// ==============================
async function cargarProductos() {
  const respuesta = await fetch(`${API_URL}/productos`);
  productos = await respuesta.json();
  if (currentUser.rol === "administrador") mostrarProductos();
}

async function cargarInventario() {
  const respuesta = await fetch(`${API_URL}/inventario`);
  inventario = await respuesta.json();
  if (currentUser.rol === "gerente" || currentUser.rol === "administrador") {
    mostrarInventario();
  }
}

async function cargarEstadisticas() {
  const respuesta = await fetch(`${API_URL}/estadisticas`);
  const stats = await respuesta.json();
  document.getElementById("statProductos").textContent = stats.productos;
  document.getElementById("statInventarios").textContent = stats.inventarios;
  document.getElementById("statTransacciones").textContent = stats.transacciones;
}

async function cargarGanancias() {
  const respuesta = await fetch(`${API_URL}/ganancias`);
  const ganancias = await respuesta.json();
  const tabla = document.getElementById("tablaGanancias");
  tabla.innerHTML = "";

  ganancias.forEach((g) => {
    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${g.sucursal_nombre}</td>
      <td>$${g.ingresos_totales.toLocaleString("es-CL")}</td>
    `;
    tabla.appendChild(fila);
  });
}

async function cargarTransacciones() {
  const respuesta = await fetch(`${API_URL}/transacciones`);
  const transacciones = await respuesta.json();
  const tabla = document.getElementById("tablaTransacciones");
  tabla.innerHTML = "";

  transacciones.forEach((t) => {
    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${t.fecha}</td>
      <td>${t.sucursal_nombre}</td>
      <td>${t.producto}</td>
      <td class="tag-${t.tipo}">${t.tipo}</td>
      <td>${t.cantidad}</td>
      <td>${t.motivo}</td>
    `;
    tabla.appendChild(fila);
  });
}

// ==============================
// Vista ADMINISTRADOR: productos
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
      <td><button class="btn-eliminar" onclick="eliminarProducto(${producto.sku_id})">Eliminar</button></td>
    `;
    tabla.appendChild(fila);
  });
}

async function agregarProducto(evento) {
  evento.preventDefault();

  const nombre = document.getElementById("nombre").value.trim();
  const categoria = document.getElementById("categoria").value.trim();
  const stock = document.getElementById("stock").value.trim();

  if (!nombre || !categoria || !stock) {
    alert("Complete todos los campos");
    return;
  }

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
}

async function eliminarProducto(sku_id) {
  await fetch(`${API_URL}/productos/${sku_id}`, { method: "DELETE" });
  await cargarProductos();
}

function buscarProducto() {
  const texto = document.getElementById("busqueda").value.toLowerCase();
  document.querySelectorAll("#tablaProductos tr").forEach((fila) => {
    fila.style.display = fila.textContent.toLowerCase().includes(texto) ? "" : "none";
  });
}

// ==============================
// Vista GERENTE: inventario por sucursal
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
// Vista REPONEDOR: mapa de la sucursal
// ==============================
function dibujarMapa() {
  document.getElementById("mapaSucursal").innerHTML = `
    <svg viewBox="0 0 700 500" xmlns="http://www.w3.org/2000/svg">
      <rect x="20" y="20" width="650" height="440" rx="55" fill="none" stroke="#333" stroke-width="4"/>

      <rect id="zona-congelados" class="zona" x="170" y="55" width="150" height="45"/>
      <text class="zona-texto" x="245" y="78">Congelados</text>

      <rect id="zona-bebidas" class="zona" x="340" y="55" width="150" height="45"/>
      <text class="zona-texto" x="415" y="78">Bebidas</text>

      <rect id="zona-lacteos" class="zona" x="65" y="105" width="50" height="130"/>
      <text class="zona-texto" x="90" y="170" transform="rotate(-90 90 170)">Lácteos</text>

      <rect id="zona-refrigerios" class="zona" x="555" y="105" width="50" height="130"/>
      <text class="zona-texto" x="580" y="170" transform="rotate(-90 580 170)">Refrigerios</text>

      <rect id="zona-golosinas" class="zona" x="255" y="185" width="40" height="100"/>
      <text class="zona-texto" x="275" y="235" transform="rotate(-90 275 235)">Golosinas</text>

      <rect id="zona-alcohol" class="zona" x="305" y="185" width="210" height="45"/>
      <text class="zona-texto" x="410" y="208">Alcohol</text>

      <rect id="zona-condimentos" class="zona" x="305" y="240" width="210" height="45"/>
      <text class="zona-texto" x="410" y="263">Condimentos</text>

      <rect id="zona-conservas" class="zona" x="555" y="245" width="50" height="140"/>
      <text class="zona-texto" x="580" y="315" transform="rotate(-90 580 315)">Conservas</text>

      <rect id="zona-panaderia" class="zona" x="280" y="380" width="240" height="50"/>
      <text class="zona-texto" x="400" y="405">Panadería</text>

      <rect class="zona" x="140" y="250" width="70" height="45"/>
      <text class="zona-texto" x="175" y="272">Cajero</text>

      <text x="60" y="330" font-size="12" fill="#333">Entrada y salida</text>
      <line x1="55" y1="300" x2="90" y2="300" stroke="#333" stroke-width="3" marker-end="url(#flecha)"/>

      <defs>
        <marker id="flecha" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
          <path d="M0,0 L8,4 L0,8 Z" fill="#333"/>
        </marker>
      </defs>
    </svg>
  `;
}

// Marca en rojo las zonas donde hay productos bajo el stock mínimo, para la sucursal del reponedor
function mostrarAlertasReponedor() {
  const sucursalId = currentUser.sucursal_id;
  const contenedor = document.getElementById("listaAlertas");
  contenedor.innerHTML = "";

  const itemsSucursal = inventario.filter((i) => i.sucursal_id === sucursalId);
  const alertas = [];

  itemsSucursal.forEach((item) => {
    const producto = productos.find((p) => p.sku_id === item.sku_id);
    if (producto && item.cantidad_disponible < producto.stock_minimo) {
      alertas.push({ item, producto });

      const zonaId = CATEGORIA_A_ZONA[producto.categoria];
      const zonaEl = zonaId ? document.getElementById(zonaId) : null;
      if (zonaEl) zonaEl.classList.add("alerta-bajo");
    }
  });

  if (alertas.length === 0) {
    contenedor.innerHTML = `<p class="sin-alertas">No hay productos bajo el stock mínimo en tu sucursal ahora mismo.</p>`;
    return;
  }

  alertas.forEach(({ item, producto }) => {
    const fila = document.createElement("div");
    fila.className = "alerta-item";
    fila.innerHTML = `
      <strong>${producto.nombre}</strong>
      <span>Zona: ${producto.categoria}</span>
      <span>Quedan ${item.cantidad_disponible} (mínimo ${producto.stock_minimo})</span>
      <input type="number" min="1" value="10" id="cantidad-${item.sku_id}">
      <button onclick="registrarMovimiento(${item.sucursal_id}, ${item.sku_id}, 'entrada')">Reponer</button>
    `;
    contenedor.appendChild(fila);
  });
}

async function registrarMovimiento(sucursalId, skuId, tipo) {
  const cantidad = Number(document.getElementById(`cantidad-${skuId}`).value);

  await fetch(`${API_URL}/inventario/${sucursalId}/${skuId}/movimiento`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      tipo,
      cantidad,
      motivo: tipo === "entrada" ? "Reposición de tienda" : "Retiro de tienda",
    }),
  });

  // recarga el inventario y vuelve a pintar el mapa con los datos actualizados
  await cargarInventario();
  dibujarMapa();
  mostrarAlertasReponedor();
}
