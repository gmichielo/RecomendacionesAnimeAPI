API_RecomendacionesAnimes — Proyecto Python + Flask + MySQL
============================================================

API / Modelo de recomendación de animes con Python y MySQL

Un proyecto que combina una API en Flask que crea un modelo de recomendaciones de animes utilizando bases de datos .csv, junto con un programa principal en Python que permite al usuario obtener recomendaciones personalizadas.
Además, incluye un sistema básico de logins conectado a una base de datos MySQL.

------------------------------------------------------------
Autores
------------------------------------------------------------
- David López García
- Gabriel

------------------------------------------------------------
Librerias utilizadas
------------------------------------------------------------
- Python
- MySQL
- API Flask
- Pandas
- Numpy
- Bcrypt

------------------------------------------------------------
Requisitos previos
------------------------------------------------------------
Asegúrate de tener instalado:

- Python 3.10 o superior
- MySQL Server / MySQL Workbench

Librerías necesarias (instálalas con PIP):

    pip install flask mysql-connector-python pandas numpy bcrypt

------------------------------------------------------------
Pasos a seguir
------------------------------------------------------------
1. Clonar o descomprimir el repositorio.
   Descarga el proyecto y ubícate en la rama principal (main) o la carpeta raíz.

2. Base de datos MySQL
   - Descarga el dump de la base de datos:
     logins_users_recomendaciones_animes.sql
     (ubicado en la carpeta Documentos)
   - Ejecútalo en MySQL Workbench para crear la base 'logins_api_anime'.

3. Archivos CSV del modelo
   - Descarga los datasets necesarios desde Google Drive:
     https://drive.google.com/drive/folders/19-ttX4RteFSeT0RUCn4AvREzGHLW08ha?usp=drive_link
   - Colócalos dentro de la carpeta BackEnd.

4. Iniciar la API Flask
   Abre una terminal en la carpeta BackEnd y ejecuta:

       flask --app API_RecomendacionesAnimes run

   o alternativamente:

       python API_RecomendacionesAnimes.py

   Esto lanzará la API local en:
       http://127.0.0.1:5000

5. Ejecutar el programa principal
   Abre el archivo FrontEnd/main.py y ejecútalo en una terminal aparte:

       python FrontEnd/main.py

6. Iniciar sesión o registrarse
   - Asegúrate de que MySQL esté iniciado y accesible.
   - Usa el sistema de login del programa (usuario y contraseña base en Documentos/usuario_contrasenya_base.txt).

------------------------------------------------------------
Aclaraciones importantes
------------------------------------------------------------
1. Orden de ejecución:
   - Inicia primero la base de datos MySQL, luego la API Flask, y finalmente el main.py.

2. Tiempo de carga inicial:
   - La primera vez que ejecutes el algoritmo, puede tardar entre 4 y 5 minutos mientras se genera el modelo de correlación.
   - En ejecuciones posteriores, el tiempo se reduce a segundos.

3. Cierre del sistema:
   - Para detener la API, vuelve a la terminal donde se está ejecutando y presiona Ctrl + C.

------------------------------------------------------------
Estructura del proyecto
------------------------------------------------------------
RecomendacionesAnimeAPI (branch Vers_conAPI)
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
├── Documentos/
│   ├── Diagramas_API_RecomendacionAnimes.png
│   ├── logins_users_recomendaciones_animes.sql
│   ├── usuario_contrasenya_base.txt
│   └── README.txt
│
├── static/
│   └── gif/
│
├── templates/
│   └── index.html
│
└── README.md
