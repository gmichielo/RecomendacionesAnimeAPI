# 🧠 API_RecomendacionesAnimes — Proyecto Python + Flask + MySQL

## Descripción
API / Modelo de recomendación de animes desarrollado con **Python**, **Flask** y **MySQL**.

El proyecto combina:
- Una **API Flask** que crea y sirve un modelo de recomendaciones de animes basado en datos `.csv`.
- Una **interfaz web** (HTML/JS) que permite:
  - Conectarse a una base de datos MySQL.
  - **Registrar** nuevos usuarios (con contraseñas cifradas mediante *bcrypt*).
  - **Iniciar sesión** con validación real.
  - Entrenar el modelo y obtener recomendaciones personalizadas desde el navegador.

## 👥 Autores
- **David López García**
- **Gabriel**

## ⚙️ Librerías utilizadas
- **Python**
- **Flask (API Web)**
- **Flask-cors**
- **MySQL Connector**
- **Pandas**
- **NumPy**
- **Bcrypt**
- **Bootstrap 5 (Frontend)**
- **Fuse.js (buscador inteligente de animes)**

## 🧩 Requisitos previos

### Aplicaciones necesarias
- **Python 3.10+**
- **MySQL Server / MySQL Workbench**

### Librerías de Python
Instálalas con:

```bash
pip install flask flask-cors mysql-connector-python pandas numpy bcrypt
```

## 🚀 Pasos para ejecutar el proyecto

### 1️⃣ Clonar o descomprimir el proyecto
Descarga el repositorio o ZIP y colócalo en una carpeta local.

### 2️⃣ Configurar la base de datos MySQL
1. Abre **MySQL Workbench**.  
2. Crea una base de datos llamada:
   ```sql
   CREATE DATABASE logins_api_anime;
   USE logins_api_anime;
   ```
3. Crea la tabla de usuarios:
   ```sql
   CREATE TABLE usuario_contrasenyas (
     idUsuario_contrasenya INT AUTO_INCREMENT PRIMARY KEY,
     usuario VARCHAR(100) NOT NULL UNIQUE,
     contrasenya VARCHAR(255) NOT NULL
   );
   ```
4. (Opcional) Puedes importar el dump incluido en:
   ```
   Documentos/logins_users_recomendaciones_animes.sql
   ```

### 3️⃣ Colocar los archivos CSV del modelo
Descarga los datasets desde Google Drive:

🔗 [Dataset de entrenamiento (anime.csv, rating.csv)](https://drive.google.com/drive/folders/19-ttX4RteFSeT0RUCn4AvREzGHLW08ha?usp=drive_link)

Colócalos dentro de la carpeta:
```
BackEnd/
```

### 4️⃣ Iniciar la API Flask
Abre una terminal en la carpeta `BackEnd` y ejecuta:

```bash
flask --app API_RecomendacionesAnimes run
```
O alternativamente:
```bash
python API_RecomendacionesAnimes.py
```

Esto levantará la aplicación en:
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

### 5️⃣ Conectarte desde la interfaz web
Abre en tu navegador:
```
http://127.0.0.1:5000
```
1. En la **pantalla inicial**, introduce tus credenciales MySQL:
   - Host: `localhost`
   - Usuario: `root`
   - Contraseña: *(la tuya)*
   - Base de datos: `logins_api_anime`
2. Pulsa **“Conectar a MySQL”** → si la conexión es correcta, se habilitará el login.

### 6️⃣ Login y registro
- Si ya tienes un usuario → inicia sesión.  
- Si no → regístrate directamente desde la web.  
  - Las contraseñas se guardan **encriptadas con bcrypt** en MySQL.
  - Verás mensajes visuales de éxito o error en pantalla.

### 7️⃣ Entrenamiento del modelo
Una vez logueado:
- Usa el botón 🧠 **Entrenar modelo** para crear o actualizar el modelo de correlación.  
  La primera vez puede tardar **4–5 minutos**.  
  En ejecuciones posteriores, se carga en segundos.

### 8️⃣ Obtener recomendaciones
- Valora varios animes introduciendo su **ID y calificación (1–10)**.
- Pulsa **✨ Obtener Recomendaciones**.
- Se mostrarán tus recomendaciones personalizadas con imágenes, sinopsis y puntuaciones obtenidas desde la API pública *Jikan*.

## 🧱 Estructura del proyecto

```
RecomendacionesAnimeAPI/
│
├── BackEnd/
│   ├── anime.csv
│   ├── rating.csv
│   └── API_RecomendacionesAnimes.py
│
├── FrontEnd/
│   ├── DAO_Logins.py
│   ├── Usuario_Contrasenya.py
│   └── main.py
│
├── templates/
│   └── index.html
│
├── static/
│   └── gif/
│       ├── entrenando.gif
│       ├── goku.gif
│       └── noimage.png
│
├── Documentos/
│   ├── Diagramas_API_RecomendacionAnimes.png
│   ├── logins_users_recomendaciones_animes.sql
│   ├── usuario_contrasenya_base.txt
│   └── README.txt
│
└── README.md
```

## 💡 Aclaraciones importantes

1. **Orden de ejecución:**
   - Arranca primero MySQL.  
   - Luego ejecuta Flask.  
   - Finalmente abre la web o el main.py (si usas el cliente de consola).

2. **Tiempo de entrenamiento inicial:**
   - Puede tardar varios minutos la primera vez.  
   - En siguientes ejecuciones, se carga el modelo guardado (`modelo_corrMatrix.pkl`).

3. **Mensajes visuales en la web:**
   - Errores y validaciones se muestran directamente en pantalla (no se usan alertas del navegador).

4. **Cierre del servidor:**
   - Pulsa `Ctrl + C` en la terminal para detener Flask.
