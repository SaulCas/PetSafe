/*
Este archivo controla el mapa interactivo, los filtros y el formulario
de creación de reportes desde el frontend.
*/

let mapa;
let marcadorSeleccionado = null;
let circuloSeleccionado = null;
let capaReportes;
let marcadorUbicacionUsuario = null;


function iniciarMapa() {
    /* Crea el mapa principal y define una vista inicial amigable. */
    mapa = L.map("mapa").setView([19.4326, -99.1332], 12);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
    }).addTo(mapa);

    capaReportes = L.layerGroup().addTo(mapa);
    mapa.on("click", manejarClickMapa);
}


function usarUbicacionActual() {
    /* Pide permiso al navegador para centrar el mapa en la ubicación real del usuario. */
    const mensajeUbicacion = document.getElementById("mensaje-ubicacion");

    if (!navigator.geolocation) {
        mensajeUbicacion.textContent =
            "Tu navegador no permite obtener la ubicación. Puedes seguir usando el mapa normal.";
        return;
    }

    mensajeUbicacion.textContent = "Buscando tu ubicación...";

    navigator.geolocation.getCurrentPosition(
        (posicion) => {
            const latitud = posicion.coords.latitude;
            const longitud = posicion.coords.longitude;

            mapa.setView([latitud, longitud], 15);

            if (marcadorUbicacionUsuario) {
                marcadorUbicacionUsuario.setLatLng([latitud, longitud]);
            } else {
                marcadorUbicacionUsuario = L.marker([latitud, longitud]).addTo(mapa);
                marcadorUbicacionUsuario.bindPopup("Estás aquí.");
            }

            mensajeUbicacion.textContent = "Ubicación encontrada. El mapa se centró en tu zona.";
        },
        () => {
            mensajeUbicacion.textContent =
                "No se pudo usar tu ubicación o no diste permiso. El mapa sigue funcionando normal.";
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0,
        }
    );
}


function manejarClickMapa(evento) {
    /* Coloca un pin temporal cuando el usuario elige la ubicación del reporte. */
    const { lat, lng } = evento.latlng;

    document.getElementById("latitud").value = lat.toFixed(6);
    document.getElementById("longitud").value = lng.toFixed(6);
    document.getElementById("mensaje-formulario").textContent =
        `Ubicación elegida: ${lat.toFixed(4)}, ${lng.toFixed(4)}.`;

    if (marcadorSeleccionado) {
        marcadorSeleccionado.setLatLng([lat, lng]);
    } else {
        marcadorSeleccionado = L.marker([lat, lng]).addTo(mapa);
    }

    actualizarCirculoTemporal();
}


function actualizarCirculoTemporal() {
    /* Dibuja o actualiza el círculo del radio de búsqueda elegido. */
    if (!marcadorSeleccionado) {
        return;
    }

    const radioMetros = Number(document.getElementById("radio_busqueda_metros").value);
    const coordenadas = marcadorSeleccionado.getLatLng();

    if (circuloSeleccionado) {
        circuloSeleccionado.setLatLng(coordenadas);
        circuloSeleccionado.setRadius(radioMetros);
    } else {
        circuloSeleccionado = L.circle(coordenadas, {
            radius: radioMetros,
            color: "#dd7f4b",
            fillColor: "#f2b995",
            fillOpacity: 0.25,
        }).addTo(mapa);
    }
}


function obtenerColoresMarcados(nombreCampo) {
    /* Devuelve todos los colores seleccionados en un grupo de checkboxes. */
    return Array.from(document.querySelectorAll(`input[name="${nombreCampo}"]:checked`)).map(
        (checkbox) => checkbox.value
    );
}


async function cargarReportes() {
    /* Consulta los reportes activos del backend y los dibuja en el mapa. */
    const tipo = document.getElementById("filtro-tipo").value;
    const colores = obtenerColoresMarcados("colores");
    const parametros = new URLSearchParams();

    if (tipo) {
        parametros.append("tipo", tipo);
    }

    colores.forEach((color) => parametros.append("colores", color));

    const respuesta = await fetch(`${window.PETSAFE_CONFIG.endpointReportes}?${parametros.toString()}`);
    const datos = await respuesta.json();

    capaReportes.clearLayers();

    if (!datos.ok) {
        document.getElementById("mensaje-filtros").textContent = "No se pudieron cargar los reportes.";
        return;
    }

    if (datos.reportes.length === 0) {
        document.getElementById("mensaje-filtros").textContent = "No hay resultados con esos filtros.";
        return;
    }

    document.getElementById("mensaje-filtros").textContent =
        `Se encontraron ${datos.reportes.length} reporte(s).`;

    datos.reportes.forEach((reporte) => {
        const marcador = L.marker([reporte.latitud, reporte.longitud]).addTo(capaReportes);
        const circulo = L.circle([reporte.latitud, reporte.longitud], {
            radius: reporte.radio_busqueda_metros,
            color: "#5c8ecb",
            fillColor: "#8fb3df",
            fillOpacity: 0.16,
        }).addTo(capaReportes);

        marcador.bindPopup(crearContenidoPopup(reporte));
        circulo.bindPopup(crearContenidoPopup(reporte));
    });
}


function crearContenidoPopup(reporte) {
    /* Genera el contenido HTML que se ve al abrir un pin del mapa. */
    const recompensa = reporte.ofrece_recompensa ? "Sí" : "No";
    const colores = (reporte.colores_visibles || reporte.colores.map((color) => capitalizar(color))).join(", ");
    const bloqueImagen = reporte.foto_url
        ? `<img class="imagen-popup" src="${reporte.foto_url}" alt="Foto de ${reporte.nombre_mascota}">`
        : `<p class="mensaje-suave">Sin imagen disponible.</p>`;
    const botonContacto = reporte.usuario_id === window.PETSAFE_CONFIG.usuarioActualId
        ? `<button class="boton-secundario" type="button" disabled>Tu reporte</button>`
        : `<a class="boton-secundario boton-contacto" href="${reporte.url_contacto}">Contactar</a>`;

    return `
        <div class="popup-reporte">
            <h3>${reporte.nombre_mascota}</h3>
            ${bloqueImagen}
            <p><span class="etiqueta">Edad:</span> ${reporte.edad_mascota}</p>
            <p><span class="etiqueta">Tipo:</span> ${capitalizar(reporte.tipo_visible)}</p>
            <p><span class="etiqueta">Colores:</span> ${colores}</p>
            <p><span class="etiqueta">Descripción:</span> ${reporte.descripcion}</p>
            <p><span class="etiqueta">Radio:</span> ${reporte.radio_busqueda_metros} m</p>
            <p><span class="etiqueta">Recompensa:</span> ${recompensa}</p>
            <p><span class="etiqueta">Publicado por:</span> ${reporte.usuario_creador}</p>
            ${botonContacto}
        </div>
    `;
}


function capitalizar(texto) {
    /* Convierte la primera letra a mayúscula para mostrar textos más amigables. */
    if (!texto) {
        return "";
    }
    return texto.charAt(0).toUpperCase() + texto.slice(1);
}


async function enviarReporte(evento) {
    /* Envía el formulario al backend y actualiza el mapa si todo sale bien. */
    evento.preventDefault();

    const latitud = document.getElementById("latitud").value;
    const longitud = document.getElementById("longitud").value;

    if (!latitud || !longitud) {
        document.getElementById("mensaje-formulario").textContent =
            "Primero debes hacer clic en el mapa para elegir la ubicación.";
        return;
    }

    const datos = new FormData();
    datos.append("nombre_mascota", document.getElementById("nombre_mascota").value.trim());
    datos.append("edad_mascota", document.getElementById("edad_mascota").value.trim());
    datos.append("tipo_mascota", document.getElementById("tipo_mascota").value);
    datos.append("otro_tipo_mascota", document.getElementById("otro_tipo_mascota").value.trim());
    datos.append("descripcion", document.getElementById("descripcion").value.trim());
    datos.append("radio_busqueda_metros", document.getElementById("radio_busqueda_metros").value);
    datos.append("ofrece_recompensa", document.getElementById("ofrece_recompensa").checked);
    datos.append("latitud", latitud);
    datos.append("longitud", longitud);

    obtenerColoresMarcados("colores_reporte").forEach((color) => {
        datos.append("colores", color);
    });

    const archivoFoto = document.getElementById("foto_mascota").files[0];
    if (archivoFoto) {
        datos.append("foto_mascota", archivoFoto);
    }

    const respuesta = await fetch(window.PETSAFE_CONFIG.endpointCrearReporte, {
        method: "POST",
        body: datos,
    });

    const resultado = await respuesta.json();
    document.getElementById("mensaje-formulario").textContent = resultado.mensaje;

    if (!resultado.ok) {
        return;
    }

    document.getElementById("formulario-reporte").reset();
    document.getElementById("valor-radio").textContent = "300 m";
    document.getElementById("contenedor-otro-tipo").classList.add("oculto");
    document.getElementById("latitud").value = "";
    document.getElementById("longitud").value = "";

    if (marcadorSeleccionado) {
        mapa.removeLayer(marcadorSeleccionado);
        marcadorSeleccionado = null;
    }

    if (circuloSeleccionado) {
        mapa.removeLayer(circuloSeleccionado);
        circuloSeleccionado = null;
    }

    await cargarReportes();
}


function activarControlesFormulario() {
    /* Conecta eventos visuales del formulario para mejorar la experiencia. */
    const selectorTipo = document.getElementById("tipo_mascota");
    const contenedorOtroTipo = document.getElementById("contenedor-otro-tipo");
    const inputOtroTipo = document.getElementById("otro_tipo_mascota");
    const controlRadio = document.getElementById("radio_busqueda_metros");
    const etiquetaRadio = document.getElementById("valor-radio");
    const botonUbicacion = document.getElementById("boton-ubicacion");

    selectorTipo.addEventListener("change", () => {
        if (selectorTipo.value === "otro") {
            contenedorOtroTipo.classList.remove("oculto");
            inputOtroTipo.required = true;
        } else {
            contenedorOtroTipo.classList.add("oculto");
            inputOtroTipo.required = false;
            inputOtroTipo.value = "";
        }
    });

    controlRadio.addEventListener("input", () => {
        etiquetaRadio.textContent = `${controlRadio.value} m`;
        actualizarCirculoTemporal();
    });

    document
        .getElementById("formulario-reporte")
        .addEventListener("submit", enviarReporte);

    document.getElementById("formulario-filtros").addEventListener("submit", async (evento) => {
        evento.preventDefault();
        await cargarReportes();
    });

    botonUbicacion.addEventListener("click", usarUbicacionActual);
}


document.addEventListener("DOMContentLoaded", async () => {
    /* Inicia toda la lógica del frontend cuando la página ya está lista. */
    iniciarMapa();
    activarControlesFormulario();
    await cargarReportes();
});
