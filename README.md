# PetSafe

PetSafe es una aplicación web para el reporte y consulta de mascotas extraviadas mediante un mapa interactivo. El sistema permite que los usuarios se registren, inicien sesión, publiquen reportes con información detallada de la mascota, suban una imagen, consulten otros reportes, contacten al dueño por mensajería interna y administren el estado de sus propios reportes.

---

## Tabla de contenido

- [Descripción del proyecto](#descripción-del-proyecto)
- [Objetivo general](#objetivo-general)
- [Objetivos específicos](#objetivos-específicos)
- [Características principales](#características-principales)
- [Tecnologías utilizadas](#tecnologías-utilizadas)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Descripción de archivos principales](#descripción-de-archivos-principales)
- [Modelo general de funcionamiento](#modelo-general-de-funcionamiento)
- [Base de datos](#base-de-datos)
- [Estados de los reportes](#estados-de-los-reportes)
- [Instalación y ejecución local](#instalación-y-ejecución-local)
- [Uso del sistema](#uso-del-sistema)
- [Estado actual del proyecto](#estado-actual-del-proyecto)
- [Repositorio y documentación](#repositorio-y-documentación)
- [Autores](#autores)

---

## Descripción del proyecto

PetSafe fue desarrollado como una aplicación web orientada al apoyo en la localización de mascotas extraviadas. La idea principal del sistema es ofrecer una herramienta visual y práctica, basada en un mapa interactivo real, para que los usuarios puedan registrar reportes de mascotas perdidas y consultar reportes publicados por otros usuarios.

Cada reporte aparece en el mapa mediante un pin. Al seleccionar un pin, el sistema muestra la información de la mascota, su imagen si existe, el radio de búsqueda y la opción de contacto mediante mensajería interna.

Además del registro y consulta de reportes, el sistema permite administrar el estado de cada publicación sin borrar físicamente los datos, conservar historial, manejar inactividad y reactivar reportes cuando sea necesario.

---

## Objetivo general

Desarrollar una aplicación web que permita registrar, visualizar, consultar y administrar reportes de mascotas extraviadas en un mapa interactivo, integrando autenticación de usuarios, imágenes, mensajería interna y control de estado de reportes.

---

## Objetivos específicos

- Implementar registro, inicio y cierre de sesión de usuarios.
- Permitir la creación de reportes desde un mapa interactivo.
- Registrar la ubicación geográfica del último avistamiento de la mascota.
- Capturar información relevante como nombre, edad, tipo, colores, descripción, recompensa e imagen.
- Mostrar un radio de búsqueda visual sobre el mapa.
- Permitir la consulta de reportes mediante filtros por tipo y color.
- Integrar mensajería interna por reporte entre usuarios.
- Permitir al usuario administrar sus propios reportes y su estado.
- Mantener historial de reportes sin borrado físico de la base de datos.

---

## Características principales

### 1. Registro e inicio de sesión
El sistema permite:
- registro de usuarios con nombre, correo electrónico y contraseña
- inicio de sesión
- cierre de sesión
- validación de correos duplicados
- almacenamiento seguro de contraseñas mediante hash

### 2. Mapa interactivo
Después del login, el usuario accede a una pantalla principal con un mapa real implementado con Leaflet y OpenStreetMap.

### 3. Creación de reportes
Desde el mapa, el usuario puede crear un reporte de mascota extraviada capturando:
- nombre de la mascota
- edad
- tipo de mascota
- uno o más colores
- descripción
- ubicación del último avistamiento
- radio de búsqueda
- recompensa opcional
- imagen opcional

### 4. Tipos de mascota
El sistema contempla tres opciones:
- perro
- gato
- otro

Cuando el usuario selecciona **otro**, se habilita un campo adicional para especificar el tipo de mascota.

### 5. Colores múltiples
Cada reporte permite seleccionar uno o más colores de entre las opciones predefinidas:
- Café
- Negro
- Blanco
- Gris
- Beige
- Dorado
- Amarillo
- Naranja
- Crema
- Manchado
- Atigrado

### 6. Radio de búsqueda
El radio de búsqueda:
- se maneja en **metros**
- avanza de **50 en 50 metros**
- se muestra visualmente en pantalla
- dibuja un círculo en el mapa para representar el área aproximada de búsqueda

### 7. Imágenes en reportes
El sistema permite:
- subir una imagen opcional al crear el reporte
- aceptar formatos JPG, JPEG y PNG
- guardar la imagen en una carpeta local del proyecto
- mostrar la imagen en el popup del reporte
- mostrar el texto **“Sin imagen disponible”** cuando no exista imagen

### 8. Visualización de reportes
Los reportes aparecen como pines sobre el mapa. Al hacer clic en un pin, el sistema muestra un popup con:
- información de la mascota
- imagen si existe
- datos relevantes del reporte
- botón **Contactar** cuando aplica

### 9. Filtros de búsqueda
Los usuarios pueden filtrar reportes por:
- tipo de mascota
- uno o más colores

### 10. Mensajería interna
El sistema permite:
- abrir una conversación asociada a un reporte
- enviar mensajes al dueño del reporte
- consultar mensajes en una bandeja simple
- visualizar una conversación por reporte
- evitar que un usuario se escriba a sí mismo
- mostrar un aviso de seguridad dentro de la conversación

### 11. Geolocalización
La pantalla principal cuenta con un botón **Usar mi ubicación**, el cual:
- solicita permiso del navegador
- centra el mapa en la ubicación actual del usuario
- coloca un marcador de referencia con el texto **“Estás aquí”**
- mantiene el mapa funcional aunque el usuario niegue el permiso

### 12. Administración de reportes
El sistema cuenta con una sección de **Mis reportes**, donde el usuario puede:
- ver sus reportes
- revisar el estado actual de cada uno
- cerrar reportes
- reactivar reportes inactivos
- consultar información relacionada con inactividad y estado

### 13. Validación de contenido
El sistema incluye:
- validación de campos obligatorios
- filtro de palabras ofensivas
- validaciones visibles para el usuario
- mensajes en español con ortografía y acentos corregidos

---

## Tecnologías utilizadas

### Backend
- **Python**
- **Flask**
- **SQLite**
- **SQLAlchemy**
- **Flask-Login**
- **Werkzeug**

### Frontend
- **HTML**
- **CSS**
- **JavaScript**

### Mapa
- **Leaflet**
- **OpenStreetMap**

---

## Estructura del proyecto

```text
petsafe/
  app.py
  requirements.txt
  README.md
  abrir_petsafe.bat
  /templates
    base.html
    login.html
    registro.html
    inicio.html
    mis_mensajes.html
    conversacion.html
    mis_reportes.html
  /static
    /css
      styles.css
    /js
      mapa.js
    /img
      logo-petsafe.svg
    /fotos_mascotas
      (aquí se guardan las imágenes subidas)
  /instance
    petsafe.db
```

---

## Descripción de archivos principales

### `app.py`
Es el archivo principal del backend. Aquí se concentra:
- configuración de Flask
- conexión con SQLite
- definición de modelos
- autenticación con Flask-Login
- validaciones
- rutas HTML
- rutas API
- lógica de reportes
- lógica de mensajería
- lógica de estados, inactividad y reactivación
- compatibilidad con cambios previos de base de datos

### `requirements.txt`
Incluye las dependencias necesarias para instalar y ejecutar el proyecto.

### `README.md`
Documento de presentación, descripción técnica y guía general del proyecto.

### `abrir_petsafe.bat`
Archivo de Windows para abrir la aplicación con doble clic.

### `templates/base.html`
Plantilla base utilizada por las demás vistas HTML.

### `templates/login.html`
Vista para el inicio de sesión de los usuarios.

### `templates/registro.html`
Vista para el registro de nuevos usuarios.

### `templates/inicio.html`
Vista principal del sistema. Contiene el mapa interactivo, filtros, formulario de reportes y botón de geolocalización.

### `templates/mis_mensajes.html`
Vista de bandeja simple para consultar conversaciones.

### `templates/conversacion.html`
Vista de conversación asociada a un reporte.

### `templates/mis_reportes.html`
Vista para administrar reportes propios y sus estados.

### `static/css/styles.css`
Archivo de estilos del proyecto.

### `static/js/mapa.js`
Archivo JavaScript donde se encuentra la lógica del mapa, geolocalización, manejo de pines, filtros, slider, formulario y popups.

### `static/img/logo-petsafe.svg`
Logotipo del sistema.

### `static/fotos_mascotas/`
Carpeta donde se almacenan las imágenes subidas por los usuarios.

### `instance/petsafe.db`
Base de datos SQLite local del proyecto.

---

## Modelo general de funcionamiento

El funcionamiento general del sistema es el siguiente:

1. El usuario accede al sistema.
2. Se registra o inicia sesión.
3. Entra a la pantalla principal con el mapa interactivo.
4. Puede usar su ubicación actual para centrar el mapa.
5. Selecciona un punto en el mapa para indicar la ubicación del último avistamiento.
6. Captura los datos de la mascota extraviada.
7. Define el radio de búsqueda en metros.
8. Opcionalmente sube una imagen.
9. Publica el reporte.
10. El sistema guarda la información en la base de datos.
11. El reporte se muestra como un pin en el mapa si está en estado activo.
12. Otros usuarios pueden consultar el reporte al seleccionar el pin.
13. Si necesitan contactar al dueño, pueden usar la mensajería interna.
14. El dueño puede administrar el estado del reporte desde **Mis reportes**.

---

## Base de datos

El proyecto utiliza **SQLite** como base de datos local, ubicada en:

```text
instance/petsafe.db
```

### Tablas principales existentes

- `usuarios`
- `reportes`
- `colores`
- `reporte_colores`
- `mensajes_chat`
- `notificaciones`

### Información general almacenada

#### `usuarios`
Guarda:
- nombre
- correo
- contraseña cifrada

#### `reportes`
Guarda:
- datos generales de la mascota
- ubicación
- descripción
- radio de búsqueda
- imagen
- estado del reporte
- fechas relacionadas con actividad y control del reporte
- motivo de cierre si aplica

#### `colores`
Catálogo base de colores válidos.

#### `reporte_colores`
Relaciona un reporte con uno o varios colores.

#### `mensajes_chat`
Guarda:
- contenido del mensaje
- fecha
- reporte asociado
- remitente
- destinatario
- estado de lectura

#### `notificaciones`
Guarda avisos internos, por ejemplo los relacionados con inactividad.

---

## Estados de los reportes

El sistema no elimina físicamente los reportes como comportamiento normal del usuario. En su lugar, maneja estados.

### Estados principales
- **activo**
- **encontrada**
- **cerrado**
- **inactivo**

### Lógica general
- Solo los reportes en estado **activo** aparecen en el mapa.
- Los reportes en estado **encontrada**, **cerrado** o **inactivo** ya no aparecen en el mapa.
- Los reportes se conservan en la base de datos para historial y estadísticas.
- Los reportes inactivos pueden reactivarse para volver a mostrarse en el mapa.

### Inactividad
El sistema contempla control de inactividad:
- detecta reportes que requieren revisión
- genera avisos internos
- permite al usuario mantener activo el reporte o actualizar su estado
- oculta del mapa los reportes que pasan a estado inactivo

---

## Instalación y ejecución local

### Requisitos previos

Se recomienda tener instalado:
- Python 3
- pip
- Visual Studio Code o un editor similar
- entorno virtual de Python

---

### Opción 1: abrir con doble clic

Ejecutar:

```text
abrir_petsafe.bat
```

Este archivo:
- activa el entorno virtual
- ejecuta `python app.py`
- abre la aplicación en el navegador

---

### Opción 2: ejecución manual

#### 1. Ubicarse en la carpeta del proyecto

```powershell
cd C:\Users\saulcasas\OneDrive\Documentos\Playground\petsafe
```

#### 2. Activar el entorno virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

#### 3. Si PowerShell bloquea la activación, ejecutar primero

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Después, volver a ejecutar:

```powershell
.\.venv\Scripts\Activate.ps1
```

#### 4. Instalar dependencias si hace falta

```powershell
pip install -r requirements.txt
```

#### 5. Ejecutar la aplicación

```powershell
python app.py
```

#### 6. Abrir en el navegador

```text
http://127.0.0.1:5000
```

---

## Uso del sistema

### Registro
El usuario crea una cuenta proporcionando su nombre, correo y contraseña.

### Inicio de sesión
Una vez registrado, puede ingresar al sistema con sus credenciales.

### Crear reporte
Dentro de la pantalla principal:
- hace clic en el mapa
- llena el formulario del reporte
- selecciona tipo y colores
- define el radio de búsqueda
- opcionalmente sube una imagen
- publica el reporte

### Consultar reportes
Los reportes activos se visualizan como pines. Al hacer clic en uno, se despliega la información correspondiente.

### Filtrar resultados
Se pueden aplicar filtros para mostrar reportes según:
- tipo de mascota
- colores seleccionados

### Usar ubicación actual
El usuario puede presionar **Usar mi ubicación** para centrar el mapa en su posición.

### Enviar mensaje
Desde el popup del reporte, otro usuario puede abrir la conversación y enviar un mensaje al dueño del reporte.

### Revisar mensajes
El usuario puede entrar a **Mis mensajes** para consultar conversaciones y mensajes asociados a sus reportes.

### Administrar reportes
Desde **Mis reportes**, el usuario puede:
- revisar sus publicaciones
- ver el estado de cada una
- cerrar reportes
- reactivar reportes
- dar seguimiento a su actividad

---

## Estado actual del proyecto

Actualmente, PetSafe cuenta con:

- autenticación completa de usuarios
- mapa interactivo funcional
- creación de reportes geolocalizados
- imagen opcional en reportes
- manejo de tipo de mascota y colores múltiples
- radio de búsqueda en metros con slider de 50 en 50
- visualización de pines en el mapa
- filtros por tipo y color
- mensajería interna simple por reporte
- geolocalización del navegador
- bandeja de mensajes y vista de conversación
- administración de reportes propios
- control de estados de reportes
- inactividad, notificaciones y reactivación
- validaciones y mensajes visibles en español
- apertura fácil en Windows mediante archivo `.bat`

---

## Repositorio y documentación

Este repositorio funciona como parte de la documentación del código fuente del proyecto, permitiendo:
- registrar avances
- compartir el desarrollo con integrantes del equipo
- mantener una referencia técnica del sistema
- incluir el enlace del repositorio en el reporte técnico y la presentación

---

## Autores

- Saul Casas
- Aldair Lopez
