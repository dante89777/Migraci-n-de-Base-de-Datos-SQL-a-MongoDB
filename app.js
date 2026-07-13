const API_URL = "http://localhost:5000/api";

let currentUser = null;
let productos = [];
let inventario = [];

const CATEGORIA_A_ZONA = {
  "lácteos": "zona-lacteos",
  "panadería": "zona-panaderia",
  "condimentos": "zona-condimentos",
  "bebidas": "zona-bebidas",
  "golosinas": "zona-golosinas",
  "conservas": "zona-conservas",
  "desayuno": "zona-congelados",
};

const ZONA_NOMBRES = {
  "zona-lacteos": "Lácteos", "zona-congelados": "Congelados", "zona-bebidas": "Bebidas",
  "zona-refrigerios": "Refrigerios", "zona-golosinas": "Golosinas", "zona-alcohol": "Alcohol",
  "zona-condimentos": "Condimentos", "zona-conservas": "Conservas", "zona-panaderia": "Panadería",
};

// ==============================
// LOGIN / LOGOUT
// ==============================
document.getElementById("formLogin").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const errorEl = document.getElementById("loginError");
  errorEl.textContent = "";

  const body = {
    nombre: document.getElementById("loginNombre").value.trim(),
    apellido: document.getElementById("loginApellido").value.trim(),
    sucursal_id: document.getElementById("loginSucursal").value,
    usuario: document.getElementById("loginUsuario").value.trim(),
    password: document.getElementById("loginPassword").value,
  };

  try {
    const respuesta = await fetch(`${API_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
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

document.getElementById("btnLogout").addEventListener("click", async () => {
  if (currentUser?.asistencia_id) {
    await fetch(`${API_URL}/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ asistencia_id: currentUser.asistencia_id }),
    });
  }
  currentUser = null;
  document.getElementById("appRoot").style.display = "none";
  document.getElementById("pantallaLogin").style.display = "flex";
  document.getElementById("formLogin").reset();
});

// ==============================
// Arranque de la app
// ==============================
async function iniciarApp() {
  document.getElementById("pantallaLogin").style.display = "none";
  document.getElementById("appRoot").style.display = "block";
  document.getElementById("infoUsuario").textContent =
    `${currentUser.nombre} ${currentUser.apellido} — rol: ${currentUser.rol} — ${currentUser.sucursal_nombre}`;

  aplicarPermisosPorRol(currentUser.rol);

  await cargarProductos();
  await cargarInventario();

  if (currentUser.rol === "administrador") {
    mostrarProductos();
    document.getElementById("formProducto").addEventListener("submit", agregarProducto);
  }

  if (currentUser.rol === "gerente" || currentUser.rol === "administrador") {
    mostrarInventario();
    cargarEstadisticas();
    cargarGanancias();
    cargarTransacciones();
    cargarAsistencia();
  }

  if (currentUser.rol === "reponedor") {
    dibujarMapa("mapaSucursal");
    mostrarAlertasReponedor();
    cargarTareasReponedor();
  }

  if (currentUser.rol === "cajero") {
    poblarSelectProductos();
    document.getElementById("formVenta").addEventListener("submit", registrarVenta);
    cargarVentas();
  }

  if (currentUser.rol === "seguridad") {
    dibujarMapa("mapaSeguridad");
    const nombreZona = ZONA_NOMBRES[currentUser.zona_asignada] || "sin asignar";
    document.getElementById("zonaAsignadaTexto").textContent = `Hoy estás a cargo de vigilar: ${nombreZona}`;
    const zonaEl = document.getElementById(currentUser.zona_asignada);
    if (zonaEl) zonaEl.classList.add("zona-vigilancia");
  }

  if (currentUser.rol === "inspector") {
    document.getElementById("inspectorSucursal").value = currentUser.sucursal_id;
    document.getElementById("inspectorSucursal").addEventListener("change", mostrarInspeccion);
    mostrarInspeccion();
  }
}

function aplicarPermisosPorRol(rol) {
  document.querySelectorAll("[data-roles]").forEach((el) => {
    const permitidos = el.dataset.roles.split(",");
    el.style.display = permitidos.includes(rol) ? "" : "none";
  });
}

// ==============================
// Datos base
// ==============================
async function cargarProductos() {
  const respuesta = await fetch(`${API_URL}/productos`);
  productos = await respuesta.json();
}

async function cargarInventario() {
  const respuesta = await fetch(`${API_URL}/inventario`);
  inventario = await respuesta.json();
}

async function cargarEstadisticas() {
  const respuesta = await fetch(`${API_URL}/estadisticas`);
  const stats = await respuesta.json();
  document.getElementById("statProductos").textContent = stats.productos;
  document.getElementById("statInventarios").textContent = stats.inventarios;
  document.getElementById("statTransacciones").textContent = stats.transacciones;
}

// ==============================
// GERENTE / ADMINISTRADOR
// ==============================
async function cargarAsistencia() {
  const respuesta = await fetch(`${API_URL}/asistencia`);
  const asistencia = await respuesta.json();
  const tabla = document.getElementById("tablaAsistencia");
  tabla.innerHTML = "";

  const claseEstado = {
    "Ya ingresó": "estado-ya-ingreso",
    "Atrasado": "estado-atrasado",
    "Falta": "estado-falta",
    "Finalizó turno": "estado-finalizo",
  };

  asistencia.forEach((a) => {
    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${a.nombre}</td><td>${a.apellido}</td><td>${a.rol}</td><td>${a.sucursal_nombre}</td>
      <td>${a.hora_entrada}</td><td>${a.hora_salida}</td>
      <td><span class="estado-badge ${claseEstado[a.estado] || ""}">${a.estado}</span></td>
    `;
    tabla.appendChild(fila);
  });
}

async function cargarGanancias() {
  const respuesta = await fetch(`${API_URL}/ganancias`);
  const ganancias = await respuesta.json();
  const tabla = document.getElementById("tablaGanancias");
  tabla.innerHTML = "";
  ganancias.forEach((g) => {
    const fila = document.createElement("tr");
    fila.innerHTML = `<td>${g.sucursal_nombre}</td><td>$${g.ingresos_totales.toLocaleString("es-CL")}</td>`;
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
      <td>${t.fecha}</td><td>${t.sucursal_nombre}</td><td>${t.producto}</td>
      <td class="tag-${t.tipo}">${t.tipo}</td><td>${t.cantidad}</td><td>${t.motivo}</td>
    `;
    tabla.appendChild(fila);
  });
}

function mostrarInventario() {
  const tabla = document.getElementById("tablaInventario");
  tabla.innerHTML = "";
  inventario.forEach((item) => {
    const producto = productos.find((p) => p.sku_id === item.sku_id);
    const nombreProducto = producto ? producto.nombre : `SKU ${item.sku_id}`;
    const stockBajo = producto && item.cantidad_disponible < producto.stock_minimo;
    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${item.sucursal_nombre}</td><td>${nombreProducto}</td>
      <td class="${stockBajo ? "stock-bajo" : ""}">${item.cantidad_disponible}</td>
      <td>${item.cantidad_reservada}</td><td>${item.cantidad_en_transito}</td><td>${item.fecha_ultimo_recuento}</td>
    `;
    tabla.appendChild(fila);
  });
}

// ==============================
// ADMINISTRADOR: catálogo
// ==============================
function mostrarProductos() {
  const tabla = document.getElementById("tablaProductos");
  tabla.innerHTML = "";
  productos.forEach((producto) => {
    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${producto.sku_id}</td><td>${producto.nombre}</td><td>${producto.categoria}</td>
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
  if (!nombre || !categoria || !stock) { alert("Complete todos los campos"); return; }

  await fetch(`${API_URL}/productos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nombre, categoria, stock_minimo: Number(stock), stock_maximo: Number(stock) * 4 }),
  });
  document.getElementById("formProducto").reset();
  await cargarProductos();
  mostrarProductos();
}

async function eliminarProducto(sku_id) {
  await fetch(`${API_URL}/productos/${sku_id}`, { method: "DELETE" });
  await cargarProductos();
  mostrarProductos();
}

function buscarProducto() {
  const texto = document.getElementById("busqueda").value.toLowerCase();
  document.querySelectorAll("#tablaProductos tr").forEach((fila) => {
    fila.style.display = fila.textContent.toLowerCase().includes(texto) ? "" : "none";
  });
}

// ==============================
// MAPA (reutilizable para reponedor y seguridad)
// ==============================
function dibujarMapa(idContenedor) {
  document.getElementById(idContenedor).innerHTML = `
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
      <line x1="55" y1="300" x2="90" y2="300" stroke="#333" stroke-width="3" marker-end="url(#flecha-${idContenedor})"/>
      <defs>
        <marker id="flecha-${idContenedor}" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
          <path d="M0,0 L8,4 L0,8 Z" fill="#333"/>
        </marker>
      </defs>
    </svg>
  `;
}

// ==============================
// REPONEDOR
// ==============================
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
    contenedor.innerHTML = `<p class="sin-alertas">No hay productos bajo el stock mínimo ahora mismo.</p>`;
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
    body: JSON.stringify({ tipo, cantidad, motivo: "Reposición de tienda" }),
  });
  await cargarInventario();
  dibujarMapa("mapaSucursal");
  mostrarAlertasReponedor();
  cargarTareasReponedor();
}

async function cargarTareasReponedor() {
  const respuesta = await fetch(`${API_URL}/tareas?sucursal_id=${currentUser.sucursal_id}`);
  const tareas = await respuesta.json();
  const contenedor = document.getElementById("listaTareas");
  contenedor.innerHTML = "";

  if (tareas.length === 0) {
    contenedor.innerHTML = `<p class="sin-alertas">El inspector no te ha asignado tareas pendientes.</p>`;
    return;
  }

  tareas.forEach((t) => {
    const producto = productos.find((p) => p.sku_id === t.sku_id);
    if (producto) {
      const zonaId = CATEGORIA_A_ZONA[producto.categoria];
      const zonaEl = zonaId ? document.getElementById(zonaId) : null;
      if (zonaEl) zonaEl.classList.add("alerta-tarea");
    }
    const fila = document.createElement("div");
    fila.className = "alerta-item naranjo";
    fila.innerHTML = `
      <strong>${t.producto}</strong>
      <span>Asignado por: ${t.creado_por}</span>
      <button class="btn-secundario" onclick="completarTarea('${t._id}')">Marcar listo</button>
    `;
    contenedor.appendChild(fila);
  });
}

async function completarTarea(tareaId) {
  await fetch(`${API_URL}/tareas/${tareaId}/completar`, { method: "PATCH" });
  cargarTareasReponedor();
}

// ==============================
// CAJERO
// ==============================
function poblarSelectProductos() {
  const select = document.getElementById("ventaProducto");
  select.innerHTML = productos.map((p) => `<option value="${p.sku_id}">${p.nombre} — $${p.precio_venta}</option>`).join("");
}

async function registrarVenta(evento) {
  evento.preventDefault();
  const errorEl = document.getElementById("ventaError");
  errorEl.textContent = "";

  const sku_id = Number(document.getElementById("ventaProducto").value);
  const cantidad = Number(document.getElementById("ventaCantidad").value);
  const comprobante = document.getElementById("ventaComprobante").value.trim();

  const respuesta = await fetch(`${API_URL}/ventas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sucursal_id: currentUser.sucursal_id,
      sku_id, cantidad, comprobante,
      cajero: `${currentUser.nombre} ${currentUser.apellido}`,
    }),
  });

  const datos = await respuesta.json();
  if (!respuesta.ok) { errorEl.textContent = datos.error; return; }

  document.getElementById("formVenta").reset();
  cargarVentas();
}

async function cargarVentas() {
  const respuesta = await fetch(`${API_URL}/ventas?sucursal_id=${currentUser.sucursal_id}`);
  const ventas = await respuesta.json();
  const hoyTexto = new Date().toISOString().slice(0, 10);

  const tabla = document.getElementById("tablaVentas");
  tabla.innerHTML = "";
  ventas
    .filter((v) => v.fecha.startsWith(hoyTexto))
    .forEach((v) => {
      const fila = document.createElement("tr");
      fila.innerHTML = `
        <td>${v.fecha.slice(11)}</td><td>${v.producto}</td><td>${v.cantidad}</td>
        <td>$${v.monto_total.toLocaleString("es-CL")}</td><td>${v.comprobante}</td>
      `;
      tabla.appendChild(fila);
    });
}

// ==============================
// INSPECTOR
// ==============================
function mostrarInspeccion() {
  const sucursalId = Number(document.getElementById("inspectorSucursal").value);
  const tabla = document.getElementById("tablaInspeccion");
  tabla.innerHTML = "";

  inventario.filter((i) => i.sucursal_id === sucursalId).forEach((item) => {
    const producto = productos.find((p) => p.sku_id === item.sku_id);
    if (!producto) return;
    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${producto.nombre}</td><td>${item.cantidad_disponible}</td><td>${producto.stock_minimo}</td>
      <td><button class="btn-secundario" onclick="crearTarea(${sucursalId}, ${producto.sku_id})">Marcar para reponer</button></td>
    `;
    tabla.appendChild(fila);
  });
}

async function crearTarea(sucursalId, skuId) {
  await fetch(`${API_URL}/tareas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sucursal_id: sucursalId, sku_id: skuId, creado_por: `${currentUser.nombre} ${currentUser.apellido}` }),
  });
  document.getElementById("inspeccionMensaje").textContent = "Tarea creada. El reponedor la verá en su mapa.";
  document.getElementById("inspeccionMensaje").style.color = "#1c8a44";
  setTimeout(() => { document.getElementById("inspeccionMensaje").textContent = ""; }, 3000);
}
