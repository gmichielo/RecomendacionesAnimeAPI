API_RecomendacionesAnimes — Proyecto Python + Flask + MySQL (API/Modelo de recomendación de animes con Python y MySQL)
Un Proyecto que combina una API en Flask que crea un modelo de recomendaciones de animes con bases de datos .csv y un programa principal en Python para recomendar los animes ademas de incluir un sistema de logins basico que se guarda en una base de datos SQL 

-Autores:
Gabriel
David L

-Tecnologias Utilizadas:
º Python
º MySQL
º API Flask

-Requisitos previos:
Asegúrate de tener instalado: 
º Python 3.10+
º MySQL Server 
º Las siguientes librerias (Instálalas con: pip install + nombre de la libreria)
    flask 
    mysql-connector-python
    pickle
    pandas
    numpy
    os
    html
    random

-Pasos a seguir:
0. Obtener y clonar el Repositorio para luego ubicarte en la rama Vers_conAPI

1. Descarga el DAO de la base de datos correspondiente (logins_api_anime) y guárdalo en tu MySQL. (Carpeta de Documentos)

2. Ejecuta el API_RecomendacionesAnimes.py en la consola. Asegúrate de estar en la misma carpeta donde se encuentra el archivo API_RecomendacionesAnimes.py. (O abrirlo y ejecutarlo)
    Utiliza el siguiente comando en la consola para arrancar la API:
    flask --app API_RecomendacionesAnimes run

3. Busca y abre el main.py, y ejecuta el código en una terminal dedicada.

4. Sigue las instrucciones del main.

<Aclaración #1>: Por razones de los software utlizados de primero debes iniciar sesion en la base de datos de MySQL y luego hacer el registro con el login normal

<Aclaración #2>: Seguramente la primera vez que ejecutes el algoritmo tarde un poco por crearse el modelo aproximadamente de 4 a 5 minutos el resto de veces es apenas en segundos

5. Una vez hayas terminado, vuelve a la terminal donde está corriendo el API_RecomendacionesAnimes.py y presiona Ctrl + C para detener la ejecución de la API.

-Estructura del proyecto:
<Repos_APP_Gestion_Carreras>
    > BackEnd
        anime.csv
        API_RecomendacionesAnimes.py
        rating.csv
    > Desktop (No importa no abrir)
    > Documentos
        Diagramas_API_RecomendacionAnimes.png
        logins_users_recomendaciones_animes.sql
        usuario_contrasenya_base.txt
        README.txt
    > FrontEnd
        DAO_Logins.py
        main.py
        Usuario_Contrasenya.py
    > README.md
