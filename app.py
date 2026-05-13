"""
Archivo principal de PetSafe.

Aquí está casi todo el backend del proyecto:
- configuración
- base de datos SQLite
- modelos
- login y registro
- rutas de la página
- API de reportes
- validaciones simples

La idea es que puedas abrir este archivo y entender el flujo general
sin perderte entre muchos módulos.
"""

from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash


# Estas rutas ayudan a ubicar carpetas del proyecto de forma clara.
BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)
FOTOS_DIR = BASE_DIR / "static" / "fotos_mascotas"
FOTOS_DIR.mkdir(exist_ok=True)


# Reglas básicas del formulario.
PALABRAS_PROHIBIDAS = {
    "idiota",
    "estupido",
    "tonto",
    "imbecil",
    "pendejo",
    "cabron",
    "mierda",
}

COLORES_VALIDOS = [
    "cafe",
    "negro",
    "blanco",
    "gris",
    "beige",
    "dorado",
    "amarillo",
    "naranja",
    "crema",
    "manchado",
    "atigrado",
]
TIPOS_VALIDOS = ["perro", "gato", "otro"]
EXTENSIONES_IMAGEN_VALIDAS = {"jpg", "jpeg", "png"}
NOMBRES_VISIBLES_COLORES = {
    "cafe": "Café",
    "negro": "Negro",
    "blanco": "Blanco",
    "gris": "Gris",
    "beige": "Beige",
    "dorado": "Dorado",
    "amarillo": "Amarillo",
    "naranja": "Naranja",
    "crema": "Crema",
    "manchado": "Manchado",
    "atigrado": "Atigrado",
}


# Creamos la aplicación Flask.
app = Flask(__name__)

# Configuración simple y directa para un proyecto escolar.
app.config["SECRET_KEY"] = "petsafe-clave-local-cambiar"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{INSTANCE_DIR / 'petsafe.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


# La base de datos vive aquí mismo para no separar demasiado el proyecto.
db = SQLAlchemy(app)


# Configuramos el manejo de sesiones de usuarios.
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Debes iniciar sesión para continuar."
login_manager.login_message_category = "warning"


def ahora_utc():
    """Devuelve la fecha actual en UTC para guardar tiempos consistentes."""

    return datetime.now(timezone.utc)


# Esta tabla intermedia permite que un reporte tenga varios colores.
reporte_colores = db.Table(
    "reporte_colores",
    db.Column("reporte_id", db.Integer, db.ForeignKey("reportes.id"), primary_key=True),
    db.Column("color_id", db.Integer, db.ForeignKey("colores.id"), primary_key=True),
)


class Usuario(UserMixin, db.Model):
    """Representa a un usuario registrado en PetSafe."""

    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    creado_en = db.Column(db.DateTime(timezone=True), default=ahora_utc, nullable=False)

    reportes = db.relationship("Reporte", back_populates="creador", lazy=True)
    mensajes_enviados = db.relationship(
        "MensajeChat",
        foreign_keys="MensajeChat.remitente_id",
        back_populates="remitente",
        lazy=True,
    )
    mensajes_recibidos = db.relationship(
        "MensajeChat",
        foreign_keys="MensajeChat.destinatario_id",
        back_populates="destinatario",
        lazy=True,
    )
    notificaciones = db.relationship("Notificacion", back_populates="usuario", lazy=True)

    def establecer_password(self, password_plano):
        """Convierte la contrasena a hash antes de guardarla."""

        self.password_hash = generate_password_hash(password_plano)

    def verificar_password(self, password_plano):
        """Compara la contrasena escrita con la guardada en la base."""

        return check_password_hash(self.password_hash, password_plano)


class Color(db.Model):
    """Catalogo de colores permitidos para los reportes."""

    __tablename__ = "colores"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)


class Reporte(db.Model):
    """Guarda la informacion principal de una mascota extraviada."""

    __tablename__ = "reportes"

    id = db.Column(db.Integer, primary_key=True)
    nombre_mascota = db.Column(db.String(120), nullable=False)
    edad_mascota = db.Column(db.String(50), nullable=False)
    tipo_mascota = db.Column(db.String(50), nullable=False)
    otro_tipo_mascota = db.Column(db.String(80), nullable=True)
    descripcion = db.Column(db.Text, nullable=False)
    ofrece_recompensa = db.Column(db.Boolean, default=False, nullable=False)
    foto_mascota = db.Column(db.String(255), nullable=True)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    radio_busqueda_km = db.Column(db.Float, nullable=False, default=0.1)
    radio_busqueda_metros = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(30), default="activo", nullable=False)
    motivo_cierre = db.Column(db.String(255), nullable=True)
    creado_en = db.Column(db.DateTime(timezone=True), default=ahora_utc, nullable=False)
    actualizado_en = db.Column(db.DateTime(timezone=True), default=ahora_utc, nullable=False)
    ultima_actividad_en = db.Column(db.DateTime(timezone=True), default=ahora_utc, nullable=False)
    aviso_inactividad_en = db.Column(db.DateTime(timezone=True), nullable=True)
    fecha_limite_respuesta = db.Column(db.DateTime(timezone=True), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    creador = db.relationship("Usuario", back_populates="reportes")
    colores = db.relationship("Color", secondary=reporte_colores, lazy="joined")

    def marcar_actividad(self):
        """Actualiza fechas cuando el reporte recibe alguna accion."""

        self.ultima_actividad_en = ahora_utc()
        self.actualizado_en = ahora_utc()
        self.aviso_inactividad_en = None
        self.fecha_limite_respuesta = None

    def programar_aviso_inactividad(self):
        """Deja listas las fechas para la futura etapa de inactividad."""

        self.aviso_inactividad_en = self.ultima_actividad_en + timedelta(days=6)
        self.fecha_limite_respuesta = self.ultima_actividad_en + timedelta(days=7)

    def a_diccionario(self):
        """Convierte el reporte a un formato facil de enviar al frontend."""

        tipo_visible = self.otro_tipo_mascota if self.tipo_mascota == "otro" else self.tipo_mascota
        return {
            "id": self.id,
            "nombre_mascota": self.nombre_mascota,
            "edad_mascota": self.edad_mascota,
            "tipo_mascota": self.tipo_mascota,
            "tipo_visible": tipo_visible,
            "descripcion": self.descripcion,
            "ofrece_recompensa": self.ofrece_recompensa,
            "foto_mascota": self.foto_mascota,
            "foto_url": (
                url_for("static", filename=f"fotos_mascotas/{self.foto_mascota}")
                if self.foto_mascota
                else None
            ),
            "latitud": self.latitud,
            "longitud": self.longitud,
            "radio_busqueda_metros": self.radio_busqueda_metros,
            "estado": self.estado,
            "motivo_cierre": self.motivo_cierre,
            "usuario_id": self.usuario_id,
            "usuario_creador": self.creador.nombre,
            "url_contacto": url_for("ver_conversacion", reporte_id=self.id),
            "colores": [color.nombre for color in self.colores],
            "colores_visibles": [
                NOMBRES_VISIBLES_COLORES.get(color.nombre, color.nombre.capitalize())
                for color in self.colores
            ],
            "creado_en": self.creado_en.strftime("%Y-%m-%d %H:%M"),
        }


class MensajeChat(db.Model):
    """Tabla preparada para la siguiente etapa de chat interno."""

    __tablename__ = "mensajes_chat"

    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)
    creado_en = db.Column(db.DateTime(timezone=True), default=ahora_utc, nullable=False)
    leido = db.Column(db.Boolean, default=False, nullable=False)
    reporte_id = db.Column(db.Integer, db.ForeignKey("reportes.id"), nullable=False)
    remitente_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    remitente = db.relationship(
        "Usuario",
        foreign_keys=[remitente_id],
        back_populates="mensajes_enviados",
    )
    destinatario = db.relationship(
        "Usuario",
        foreign_keys=[destinatario_id],
        back_populates="mensajes_recibidos",
    )

    def a_diccionario(self):
        """Convierte un mensaje a un formato simple para usarlo en vistas."""

        return {
            "id": self.id,
            "contenido": self.contenido,
            "creado_en": self.creado_en.strftime("%Y-%m-%d %H:%M"),
            "remitente_id": self.remitente_id,
            "destinatario_id": self.destinatario_id,
        }


class Notificacion(db.Model):
    """Tabla preparada para futuras notificaciones internas."""

    __tablename__ = "notificaciones"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50), nullable=False, default="informativa")
    leida = db.Column(db.Boolean, default=False, nullable=False)
    creada_en = db.Column(db.DateTime(timezone=True), default=ahora_utc, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    reporte_id = db.Column(db.Integer, db.ForeignKey("reportes.id"), nullable=True)

    usuario = db.relationship("Usuario", back_populates="notificaciones")


@login_manager.user_loader
def cargar_usuario(user_id):
    """Carga el usuario guardado en la sesion."""

    return Usuario.query.get(int(user_id))


def sanitizar_texto(texto):
    """Limpia espacios y escapa HTML basico."""

    return escape((texto or "").strip())


def contiene_palabras_ofensivas(texto):
    """Detecta palabras ofensivas usando la lista basica del proyecto."""

    texto_normalizado = (texto or "").lower()
    return any(palabra in texto_normalizado for palabra in PALABRAS_PROHIBIDAS)


def validar_correo_simple(correo):
    """Hace una validacion sencilla del formato del correo."""

    correo_limpio = (correo or "").strip()
    return "@" in correo_limpio and "." in correo_limpio


def convertir_booleano(valor):
    """Convierte varios formatos comunes a verdadero o falso."""

    return str(valor).lower() in {"true", "1", "si", "on"}


def respuesta_error(mensaje, codigo=400):
    """Devuelve errores JSON con un formato simple y claro."""

    return jsonify({"ok": False, "mensaje": mensaje}), codigo


def convertir_a_utc(fecha):
    """Normaliza fechas para compararlas aunque SQLite las devuelva sin zona horaria."""

    if not fecha:
        return None
    if fecha.tzinfo is None:
        return fecha.replace(tzinfo=timezone.utc)
    return fecha


def crear_notificacion_simple(usuario_id, reporte_id, titulo, mensaje, tipo="informativa"):
    """Crea una notificación solo si no existe otra igual sin leer para ese reporte."""

    ya_existe = Notificacion.query.filter_by(
        usuario_id=usuario_id,
        reporte_id=reporte_id,
        titulo=titulo,
        leida=False,
    ).first()

    if ya_existe:
        return

    db.session.add(
        Notificacion(
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            usuario_id=usuario_id,
            reporte_id=reporte_id,
        )
    )


def marcar_notificaciones_reporte_leidas(usuario_id, reporte_id):
    """Marca como leídas las notificaciones activas ligadas a un reporte."""

    notificaciones = Notificacion.query.filter_by(
        usuario_id=usuario_id,
        reporte_id=reporte_id,
        leida=False,
    ).all()

    for notificacion in notificaciones:
        notificacion.leida = True


def revisar_inactividad_reportes():
    """Revisa reportes activos y los avisa o marca como inactivos si toca.

    Esta revisión se ejecuta al entrar a rutas normales del sistema.
    Así evitamos procesos de fondo complejos y mantenemos el proyecto escolar.
    """

    ahora = ahora_utc()
    reportes_activos = Reporte.query.filter_by(estado="activo").all()
    hubo_cambios = False

    for reporte in reportes_activos:
        ultima_actividad = convertir_a_utc(reporte.ultima_actividad_en) or ahora
        fecha_aviso = convertir_a_utc(reporte.aviso_inactividad_en)
        fecha_limite = convertir_a_utc(reporte.fecha_limite_respuesta)

        # Si el reporte ya cumplió 6 días sin actividad, generamos aviso simple.
        if fecha_aviso is None and ultima_actividad <= ahora - timedelta(days=6):
            reporte.aviso_inactividad_en = ahora
            reporte.fecha_limite_respuesta = ahora + timedelta(days=1)
            crear_notificacion_simple(
                reporte.usuario_id,
                reporte.id,
                "Reporte por inactividad",
                "Tu reporte está por quedar inactivo. Indica si sigue en búsqueda o si ya fue encontrada.",
                "inactividad",
            )
            hubo_cambios = True

        # Si ya venció el tiempo del aviso y nadie respondió, el reporte pasa a inactivo.
        fecha_limite_actual = convertir_a_utc(reporte.fecha_limite_respuesta)
        if fecha_limite_actual and fecha_limite_actual <= ahora:
            reporte.estado = "inactivo"
            reporte.motivo_cierre = "Oculto por inactividad"
            reporte.actualizado_en = ahora
            marcar_notificaciones_reporte_leidas(reporte.usuario_id, reporte.id)
            crear_notificacion_simple(
                reporte.usuario_id,
                reporte.id,
                "Reporte inactivo",
                "Tu reporte dejó de mostrarse en el mapa por inactividad. Puedes reactivarlo cuando quieras.",
                "inactividad",
            )
            hubo_cambios = True

    if hubo_cambios:
        db.session.commit()


def obtener_resumen_conversaciones(usuario_id):
    """Arma una lista simple de conversaciones del usuario autenticado.

    Una conversacion se identifica por el reporte y la otra persona involucrada.
    Esto es suficiente para una bandeja escolar simple sin meter mas tablas.
    """

    mensajes = (
        MensajeChat.query.filter(
            (MensajeChat.remitente_id == usuario_id) | (MensajeChat.destinatario_id == usuario_id)
        )
        .order_by(MensajeChat.creado_en.desc())
        .all()
    )

    conversaciones = []
    llaves_vistas = set()

    for mensaje in mensajes:
        otra_persona_id = (
            mensaje.destinatario_id if mensaje.remitente_id == usuario_id else mensaje.remitente_id
        )
        llave = (mensaje.reporte_id, otra_persona_id)
        if llave in llaves_vistas:
            continue

        llaves_vistas.add(llave)
        reporte = Reporte.query.get(mensaje.reporte_id)
        otra_persona = Usuario.query.get(otra_persona_id)

        if not reporte or not otra_persona:
            continue

        conversaciones.append(
            {
                "reporte_id": reporte.id,
                "nombre_mascota": reporte.nombre_mascota,
                "estado": reporte.estado,
                "otra_persona": otra_persona.nombre,
                "ultimo_mensaje": mensaje.contenido,
                "fecha": mensaje.creado_en.strftime("%Y-%m-%d %H:%M"),
                "url": url_for("ver_conversacion", reporte_id=reporte.id),
            }
        )

    return conversaciones


def archivo_permitido(nombre_archivo):
    """Valida que el archivo tenga una extension de imagen aceptada."""

    if "." not in nombre_archivo:
        return False
    extension = nombre_archivo.rsplit(".", 1)[1].lower()
    return extension in EXTENSIONES_IMAGEN_VALIDAS


def guardar_foto_reporte(archivo, nombre_mascota):
    """Guarda la foto del reporte en una carpeta simple dentro de static.

    Devuelve el nombre final del archivo para guardarlo en la base.
    Si no se manda archivo, devuelve None.
    """

    if not archivo or not archivo.filename:
        return None

    if not archivo_permitido(archivo.filename):
        raise ValueError("La imagen debe ser JPG, JPEG o PNG.")

    nombre_seguro = secure_filename(archivo.filename)
    extension = nombre_seguro.rsplit(".", 1)[1].lower()
    base_nombre = secure_filename(nombre_mascota) or "mascota"
    marca_tiempo = datetime.now().strftime("%Y%m%d%H%M%S%f")
    nombre_final = f"{base_nombre}_{marca_tiempo}.{extension}"
    archivo.save(FOTOS_DIR / nombre_final)
    return nombre_final


def sembrar_datos_base():
    """Crea colores base y un usuario demo si aun no existen."""

    for nombre_color in COLORES_VALIDOS:
        if not Color.query.filter_by(nombre=nombre_color).first():
            db.session.add(Color(nombre=nombre_color))

    if not Usuario.query.filter_by(correo="demo@petsafe.local").first():
        usuario_demo = Usuario(nombre="Usuario Demo", correo="demo@petsafe.local")
        usuario_demo.establecer_password("petsafe123")
        db.session.add(usuario_demo)

    db.session.commit()


def convertir_reportes_antiguos():
    """Convierte reportes viejos en kilometros a metros si la base ya existia.

    Esta funcion ayuda a no perder lo que ya estaba guardado.
    Si encuentra la columna antigua `radio_busqueda_km`, la convierte a metros.
    """

    columnas = {columna["name"] for columna in db.inspect(db.engine).get_columns("reportes")}

    if "radio_busqueda_metros" not in columnas:
        with db.engine.begin() as conexion:
            conexion.exec_driver_sql(
                "ALTER TABLE reportes ADD COLUMN radio_busqueda_metros INTEGER DEFAULT 3000"
            )
            if "radio_busqueda_km" in columnas:
                conexion.exec_driver_sql(
                    "UPDATE reportes SET radio_busqueda_metros = CAST(radio_busqueda_km * 1000 AS INTEGER)"
                )


def agregar_columna_foto_si_falta():
    """Agrega la columna de foto si la base actual aun no la tiene."""

    columnas = {columna["name"] for columna in db.inspect(db.engine).get_columns("reportes")}
    if "foto_mascota" not in columnas:
        with db.engine.begin() as conexion:
            conexion.exec_driver_sql("ALTER TABLE reportes ADD COLUMN foto_mascota VARCHAR(255)")


def agregar_columna_motivo_cierre_si_falta():
    """Agrega una columna simple para guardar el motivo de cierre del reporte."""

    columnas = {columna["name"] for columna in db.inspect(db.engine).get_columns("reportes")}
    if "motivo_cierre" not in columnas:
        with db.engine.begin() as conexion:
            conexion.exec_driver_sql("ALTER TABLE reportes ADD COLUMN motivo_cierre VARCHAR(255)")


@app.errorhandler(413)
def archivo_demasiado_grande(error):
    """Muestra un mensaje claro cuando la imagen pesa demasiado."""

    if request.path.startswith("/api/"):
        return respuesta_error("La imagen es demasiado pesada. Usa una imagen menor a 5 MB.", 413)
    flash("La imagen es demasiado pesada. Usa una imagen menor a 5 MB.", "danger")
    return redirect(url_for("inicio"))


@app.route("/")
def portada():
    """Redirige al login o al mapa dependiendo si ya hay sesion."""

    if current_user.is_authenticated:
        return redirect(url_for("inicio"))
    return redirect(url_for("login"))


@app.route("/registro", methods=["GET", "POST"])
def registro():
    """Muestra el formulario de registro y crea usuarios nuevos."""

    if current_user.is_authenticated:
        return redirect(url_for("inicio"))

    if request.method == "POST":
        nombre = sanitizar_texto(request.form.get("nombre"))
        correo = sanitizar_texto(request.form.get("correo")).lower()
        password = request.form.get("password", "").strip()

        if not nombre or not correo or not password:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template("registro.html")

        if not validar_correo_simple(correo):
            flash("Ingresa un correo electrónico válido.", "danger")
            return render_template("registro.html")

        if len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "danger")
            return render_template("registro.html")

        if Usuario.query.filter_by(correo=correo).first():
            flash("Ese correo ya está registrado.", "danger")
            return render_template("registro.html")

        usuario = Usuario(nombre=nombre, correo=correo)
        usuario.establecer_password(password)

        db.session.add(usuario)
        db.session.commit()

        flash("Tu cuenta fue creada correctamente. Ahora ya puedes iniciar sesión.", "success")
        return redirect(url_for("login"))

    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Permite entrar al sistema a un usuario ya registrado."""

    if current_user.is_authenticated:
        return redirect(url_for("inicio"))

    if request.method == "POST":
        correo = sanitizar_texto(request.form.get("correo")).lower()
        password = request.form.get("password", "").strip()

        if not correo or not password:
            flash("Debes escribir tu correo y tu contraseña.", "danger")
            return render_template("login.html")

        usuario = Usuario.query.filter_by(correo=correo).first()
        if not usuario or not usuario.verificar_password(password):
            flash("Correo o contraseña incorrectos.", "danger")
            return render_template("login.html")

        login_user(usuario)
        flash("Bienvenido a PetSafe.", "success")
        return redirect(url_for("inicio"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def cerrar_sesion():
    """Cierra la sesión del usuario actual."""

    logout_user()
    flash("Tu sesión se cerró correctamente.", "info")
    return redirect(url_for("login"))


@app.route("/inicio")
@login_required
def inicio():
    """Muestra el mapa principal con filtros y formulario de reportes."""

    revisar_inactividad_reportes()

    return render_template(
        "inicio.html",
        colores=COLORES_VALIDOS,
        colores_visibles=NOMBRES_VISIBLES_COLORES,
        tipos=TIPOS_VALIDOS,
    )


@app.route("/mis-reportes")
@login_required
def mis_reportes():
    """Muestra los reportes del usuario con su estado y acciones simples."""

    revisar_inactividad_reportes()

    reportes = (
        Reporte.query.filter_by(usuario_id=current_user.id)
        .order_by(Reporte.creado_en.desc())
        .all()
    )
    notificaciones = (
        Notificacion.query.filter_by(usuario_id=current_user.id)
        .order_by(Notificacion.creada_en.desc())
        .all()
    )
    return render_template("mis_reportes.html", reportes=reportes, notificaciones=notificaciones)


@app.route("/reportes/<int:reporte_id>/cerrar", methods=["POST"])
@login_required
def cerrar_reporte(reporte_id):
    """Cierra un reporte sin borrarlo, solo cambiando su estado."""

    reporte = Reporte.query.get_or_404(reporte_id)

    if reporte.usuario_id != current_user.id:
        flash("Solo puedes cambiar el estado de tus propios reportes.", "danger")
        return redirect(url_for("mis_reportes"))

    motivo = sanitizar_texto(request.form.get("motivo"))
    detalle_otro = sanitizar_texto(request.form.get("detalle_otro"))

    if motivo not in {"encontrada", "cerrado", "otro"}:
        flash("Selecciona un motivo válido para cerrar el reporte.", "danger")
        return redirect(url_for("mis_reportes"))

    if motivo == "otro":
        if not detalle_otro:
            flash("Escribe un motivo cuando eliges la opción 'otro'.", "danger")
            return redirect(url_for("mis_reportes"))
        if contiene_palabras_ofensivas(detalle_otro):
            flash("El motivo contiene palabras no permitidas.", "danger")
            return redirect(url_for("mis_reportes"))
        reporte.estado = "cerrado"
        reporte.motivo_cierre = detalle_otro
    elif motivo == "encontrada":
        reporte.estado = "encontrada"
        reporte.motivo_cierre = "Ya la encontré"
    else:
        reporte.estado = "cerrado"
        reporte.motivo_cierre = "No la he encontrado pero ya no deseo mantener el reporte"

    reporte.actualizado_en = ahora_utc()
    reporte.ultima_actividad_en = ahora_utc()

    db.session.commit()
    flash("El reporte se actualizó correctamente y ya no aparecerá en el mapa.", "success")
    return redirect(url_for("mis_reportes"))


@app.route("/reportes/<int:reporte_id>/responder-inactividad", methods=["POST"])
@login_required
def responder_inactividad(reporte_id):
    """Permite responder al aviso de inactividad de un reporte."""

    reporte = Reporte.query.get_or_404(reporte_id)

    if reporte.usuario_id != current_user.id:
        flash("Solo puedes responder por tus propios reportes.", "danger")
        return redirect(url_for("mis_reportes"))

    accion = request.form.get("accion")

    if accion == "seguir":
        reporte.estado = "activo"
        reporte.motivo_cierre = None
        reporte.marcar_actividad()
        reporte.programar_aviso_inactividad()
        marcar_notificaciones_reporte_leidas(current_user.id, reporte.id)
        db.session.commit()
        flash("Tu reporte sigue activo y continúa visible en el mapa.", "success")
        return redirect(url_for("mis_reportes"))

    if accion == "encontrada":
        reporte.estado = "encontrada"
        reporte.motivo_cierre = "Ya la encontré"
        reporte.actualizado_en = ahora_utc()
        reporte.ultima_actividad_en = ahora_utc()
        reporte.aviso_inactividad_en = None
        reporte.fecha_limite_respuesta = None
        marcar_notificaciones_reporte_leidas(current_user.id, reporte.id)
        db.session.commit()
        flash("El reporte cambió a encontrada y dejó de aparecer en el mapa.", "success")
        return redirect(url_for("mis_reportes"))

    flash("Selecciona una respuesta válida para la inactividad.", "danger")
    return redirect(url_for("mis_reportes"))


@app.route("/reportes/<int:reporte_id>/reactivar", methods=["POST"])
@login_required
def reactivar_reporte(reporte_id):
    """Reactiva un reporte inactivo para que vuelva a mostrarse en el mapa."""

    reporte = Reporte.query.get_or_404(reporte_id)

    if reporte.usuario_id != current_user.id:
        flash("Solo puedes reactivar tus propios reportes.", "danger")
        return redirect(url_for("mis_reportes"))

    if reporte.estado != "inactivo":
        flash("Solo los reportes inactivos pueden reactivarse.", "warning")
        return redirect(url_for("mis_reportes"))

    reporte.estado = "activo"
    reporte.motivo_cierre = None
    reporte.marcar_actividad()
    reporte.programar_aviso_inactividad()
    marcar_notificaciones_reporte_leidas(current_user.id, reporte.id)

    db.session.commit()
    flash("El reporte se reactivó correctamente y volvió al mapa.", "success")
    return redirect(url_for("mis_reportes"))


@app.route("/mis-mensajes")
@login_required
def mis_mensajes():
    """Muestra una bandeja simple con las conversaciones del usuario."""

    conversaciones = obtener_resumen_conversaciones(current_user.id)
    return render_template("mis_mensajes.html", conversaciones=conversaciones)


@app.route("/mensajes/reporte/<int:reporte_id>", methods=["GET", "POST"])
@login_required
def ver_conversacion(reporte_id):
    """Muestra y permite enviar mensajes sobre un reporte especifico."""

    reporte = Reporte.query.get_or_404(reporte_id)

    if request.method == "POST":
        if reporte.usuario_id == current_user.id:
            flash("No puedes enviarte mensajes a ti mismo desde tu propio reporte.", "warning")
            return redirect(url_for("ver_conversacion", reporte_id=reporte.id))

        contenido = sanitizar_texto(request.form.get("contenido"))

        if not contenido:
            flash("Escribe un mensaje antes de enviarlo.", "danger")
            return redirect(url_for("ver_conversacion", reporte_id=reporte.id))

        if contiene_palabras_ofensivas(contenido):
            flash("El mensaje contiene palabras no permitidas.", "danger")
            return redirect(url_for("ver_conversacion", reporte_id=reporte.id))

        mensaje = MensajeChat(
            contenido=contenido,
            reporte_id=reporte.id,
            remitente_id=current_user.id,
            destinatario_id=reporte.usuario_id,
        )

        db.session.add(mensaje)
        db.session.commit()

        flash("Mensaje enviado correctamente.", "success")
        return redirect(url_for("ver_conversacion", reporte_id=reporte.id))

    # Marcamos como leidos los mensajes recibidos por el usuario en esta conversacion.
    mensajes_pendientes = MensajeChat.query.filter_by(
        reporte_id=reporte.id,
        destinatario_id=current_user.id,
        leido=False,
    ).all()

    for mensaje in mensajes_pendientes:
        mensaje.leido = True

    if mensajes_pendientes:
        db.session.commit()

    mensajes = (
        MensajeChat.query.filter_by(reporte_id=reporte.id)
        .order_by(MensajeChat.creado_en.asc())
        .all()
    )

    # Solo permitimos ver la conversacion al dueno del reporte o a quien ya participo.
    es_dueno = reporte.usuario_id == current_user.id
    ha_participado = any(
        mensaje.remitente_id == current_user.id or mensaje.destinatario_id == current_user.id
        for mensaje in mensajes
    )

    if not es_dueno and not ha_participado:
        mensajes = []

    return render_template(
        "conversacion.html",
        reporte=reporte,
        mensajes=[mensaje.a_diccionario() for mensaje in mensajes],
        es_dueno=es_dueno,
        puede_escribir=not es_dueno,
    )


@app.route("/api/reportes", methods=["GET"])
@login_required
def listar_reportes():
    """Devuelve los reportes activos usando filtros por tipo y color."""

    revisar_inactividad_reportes()

    tipo = request.args.get("tipo", "").strip().lower()
    colores = [color.strip().lower() for color in request.args.getlist("colores")]

    consulta = Reporte.query.filter_by(estado="activo")

    if tipo in TIPOS_VALIDOS:
        consulta = consulta.filter(Reporte.tipo_mascota == tipo)

    if colores:
        consulta = consulta.join(Reporte.colores).filter(Color.nombre.in_(colores)).distinct()

    reportes = consulta.order_by(Reporte.creado_en.desc()).all()
    return jsonify({"ok": True, "reportes": [reporte.a_diccionario() for reporte in reportes]})


@app.route("/api/reportes", methods=["POST"])
@login_required
def crear_reporte():
    """Guarda un nuevo reporte creado desde el mapa."""

    # Permitimos seguir recibiendo JSON, pero ahora damos prioridad a form-data
    # para poder subir imagen junto con el resto de los datos.
    datos = request.form if request.form else (request.get_json(silent=True) or {})

    nombre_mascota = sanitizar_texto(datos.get("nombre_mascota"))
    edad_mascota = sanitizar_texto(datos.get("edad_mascota"))
    tipo_mascota = sanitizar_texto(datos.get("tipo_mascota")).lower()
    otro_tipo_mascota = sanitizar_texto(datos.get("otro_tipo_mascota"))
    descripcion = sanitizar_texto(datos.get("descripcion"))
    colores_seleccionados = datos.getlist("colores") if request.form else datos.get("colores", [])

    if not nombre_mascota or not edad_mascota or not descripcion:
        return respuesta_error("Completa todos los campos obligatorios del reporte.")

    if tipo_mascota not in TIPOS_VALIDOS:
        return respuesta_error("Selecciona un tipo de mascota valido.")

    if tipo_mascota == "otro" and not otro_tipo_mascota:
        return respuesta_error("Debes escribir el tipo de mascota cuando eliges 'otro'.")

    if contiene_palabras_ofensivas(descripcion) or contiene_palabras_ofensivas(otro_tipo_mascota):
        return respuesta_error("Se detectaron palabras no permitidas en el formulario.")

    if not isinstance(colores_seleccionados, list) or not colores_seleccionados:
        return respuesta_error("Debes elegir al menos un color.")

    colores_limpios = [str(color).strip().lower() for color in colores_seleccionados]
    if any(color not in COLORES_VALIDOS for color in colores_limpios):
        return respuesta_error("Hay colores no permitidos en la selección.")

    try:
        latitud = float(datos.get("latitud"))
        longitud = float(datos.get("longitud"))
        radio_busqueda_metros = int(datos.get("radio_busqueda_metros"))
    except (TypeError, ValueError):
        return respuesta_error("La ubicación o el radio del reporte no son válidos.")

    if not (-90 <= latitud <= 90) or not (-180 <= longitud <= 180):
        return respuesta_error("La ubicación seleccionada no es válida.")

    if radio_busqueda_metros < 50 or radio_busqueda_metros > 5000 or radio_busqueda_metros % 50 != 0:
        return respuesta_error("El radio de búsqueda debe estar entre 50 y 5000 metros, avanzando de 50 en 50.")

    try:
        foto_mascota = guardar_foto_reporte(request.files.get("foto_mascota"), nombre_mascota)
    except ValueError as error:
        return respuesta_error(str(error))
    except OSError:
        return respuesta_error("Ocurrió un error al guardar la imagen. Intenta con otra imagen.")

    reporte = Reporte(
        nombre_mascota=nombre_mascota,
        edad_mascota=edad_mascota,
        tipo_mascota=tipo_mascota,
        otro_tipo_mascota=otro_tipo_mascota if tipo_mascota == "otro" else None,
        descripcion=descripcion,
        ofrece_recompensa=convertir_booleano(datos.get("ofrece_recompensa")),
        foto_mascota=foto_mascota,
        latitud=latitud,
        longitud=longitud,
        radio_busqueda_km=radio_busqueda_metros / 1000,
        radio_busqueda_metros=radio_busqueda_metros,
        usuario_id=current_user.id,
    )

    # Primero agregamos el reporte y luego sus colores para guardar bien la relación.
    db.session.add(reporte)
    reporte.colores = Color.query.filter(Color.nombre.in_(colores_limpios)).all()
    reporte.marcar_actividad()
    reporte.programar_aviso_inactividad()
    db.session.commit()

    return jsonify(
        {
            "ok": True,
            "mensaje": "Reporte publicado correctamente.",
            "reporte": reporte.a_diccionario(),
        }
    )


with app.app_context():
    # Creamos tablas si no existen.
    db.create_all()

    # Si la base ya venia de una version anterior, adaptamos el radio a metros.
    convertir_reportes_antiguos()

    # Agregamos la columna de foto si la base actual aun no la tiene.
    agregar_columna_foto_si_falta()

    # Agregamos la columna de motivo de cierre si hace falta.
    agregar_columna_motivo_cierre_si_falta()

    # Dejamos listos colores base y el usuario demo.
    sembrar_datos_base()


if __name__ == "__main__":
    # Levantamos el servidor local para trabajar en desarrollo.
    app.run(debug=True)
