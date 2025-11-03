import requests as req
import re
import os
import time
from DAO_Logins import DAO_Logins
from Usuario_Contrasenya import Usuario_Contrasenya

CANTIDAD_ERRORES = 2
LARGO_OPCIONES_LOGIN = 2
LARGO_OPCIONES_ANIME = 4
BASE_URL = "http://localhost:5000"

user_test_ratings = {}

user_ratings_hardcore = {
    "136": 10,
    "2476": 1
}

accion_usuario = 1
accion_usuario_anime = 0

API_Animes = None

usuarios = None
usuario_API = None  
usuario_BD = None
contrasenya_BD = None

usuario_AN = None
contrasenya_AN = None

conexion_establecida = False

### Funciones nesesarias
def clear(wait=2):
    time.sleep(wait)
    os.system('cls' if os.name == 'nt' else 'clear')

def pedir_texto(prompt: str):
    while True:
        texto = input(prompt)
        if texto.strip() == "":
            print("\033[31mUsuario inválido: no puede estar vacío ni contener solo espacios. Intenta otra vez.\033[0m")
            continue
        return str(texto)

def pedir_contrasenya(prompt: str) -> str:
    while True:
        pwd = input(prompt)
        if pwd.strip() == "":
            print("\033[31mContraseña inválida: no puede estar vacía ni contener solo espacios. Intenta otra vez.\033[0m")
            continue
        return pwd
    
def pedir_anime(prompt: str):
    while True:
        texto = input(prompt).strip()
        if texto == "":
            print("\033[31mAnime inválido: no puede estar vacío.\033[0m")
            continue

        if not re.fullmatch(r"\d+", texto):
            print("\033[31mEntrada inválida: debe ser solo números, sin espacios ni caracteres especiales.\033[0m")
            continue

        return texto
    
def pedir_calificacion(prompt: str) -> int:
    while True:
        pwd = input(prompt)
        if pwd.strip() == "":
            print("\033[31mCalificación inválida: no puede estar vacía ni contener solo espacios.\033[0m")
            continue

        if not pwd.isdigit():
            print("\033[31mIngresa solo números.\033[0m")
            continue

        calificacion = int(pwd)

        if calificacion < 1 or calificacion > 10:
            print("\033[31mLa calificación debe estar entre 1 y 10.\033[0m")
            continue

        return calificacion

def verificacion_usuario_existente(user_buscar):
    indice_columna = 1
    for fila in usuarios:
        if fila[indice_columna] == user_buscar:
            return True
    return False

def mostrar_menu_acciones_animes():
    menu = ("\033[33m1.- Recomendar Animes\n"
        "2.- Entrenar Algoritmo\n"
        "3.- Obtener Version\n"
        "4.- Testear Algoritmo\n"
        "0.- Salir\033[0m\n"
    )
    return menu

def mostrar_menu_acciones_recomendar():
    menu = ("\033[33m1.- Introducir anime\n"
        "2.- Recomendar\n"
        "0.- Salir\033[0m\n"
    )
    return menu

def mostrar_menu_acciones_login():
    menu = ("\033[33m1.- Iniciar sesión\n"
        "2.- Registrarse\n"
        "0.- Salir\033[0m\n"
    )
    return menu

def mostrar_lista_animes(animes_lista):
    if not animes_lista:
        return "\033[31m[!] La lista de animes está vacía\033[0m"

    out = ["\n=== Lista de animes ==="]
    out.append(f"{'ID':>6} | {'Nombre':<40}")
    out.append("-" * 50)

    for anime in animes_lista:
        # Soporta tanto formato [id, name] como dict {'anime_id':..., 'name':...}
        if isinstance(anime, (list, tuple)) and len(anime) >= 2:
            anime_id, nombre = anime[0], anime[1]
        elif isinstance(anime, dict):
            anime_id = anime.get("anime_id", "?")
            nombre = anime.get("name", "Sin nombre")
        else:
            continue  # Ignora formatos desconocidos

        out.append(f"{anime_id:>6} | {nombre:<40}")

    return "\n".join(out)

def mostrar_lista_recomendaciones(data):
    if not data:
        return "\033[31m[!] La lista de datos está vacía\033[0m"

    out = ["\n=== Calificaciones del usuario ==="]
    for item in data.get("usuario_ratings", []):
        out.append(f"{item['anime_id']:>6} | {item['name']:<40} => {item['rating']}")

    out.append("\n=== Recomendaciones TOP 10 ===")
    for item in data.get("recomendaciones_top_10", []):
        out.append(f"{item['anime_id']:>6} | {item['name']:<40} => {round(float(item['puntaje']), 2)}")

    return "\n".join(out)

def validar_password(password):
    # Al menos 8 caracteres
    # Al menos una mayuscula
    # Al menos un caracter especial
    regex = r'^(?=.*[A-Z])(?=.*[^A-Za-z0-9]).{8,}$'
    
    return re.match(regex, password) is not None

def verificar_usuario_correcta(login):
    if DAO_logins.comprobar_usuario(login):
        return True
    else:
        return False

def verificar_contrasenya_correcta(login):
    if DAO_logins.comprobar_login(login):
        return True
    else:
        return False

###     Sección base de datos
print("\033[36mBienvenid@ al recomendador de animes 2000\n")
print("\033[36mPor favor sigue las instrucciones\033[0m\n")

print("Por favor inicia sesion en la base de datos")
usuario_BD = pedir_texto("Introduce el usuario por favor: ")
contrasenya_BD = pedir_contrasenya("Introduce la contraseña por favor: ")

DAO_logins = DAO_Logins(usuario_BD, contrasenya_BD)
DAO_logins.conectar()

if DAO_logins.get_conexion() == True: 
    usuarios = DAO_logins.ver()
    print("\n\033[36mAhora por favor escoge que deseas hacer\033[0m\n")
else: print("\033[31mConexion no hecha\033[0m")

###     Seccion Login anime
while accion_usuario != 0 and DAO_logins!= None and DAO_logins.get_conexion() == True:
    print("Opciones:")
    print(mostrar_menu_acciones_login())
    
    try:
        accion_usuario = int(input(" Elige una opción: ").strip())
    except ValueError:
        print("\033[31mOpción inválida, escribe un número.\033[0m")
        continue

    if accion_usuario > LARGO_OPCIONES_LOGIN or accion_usuario < 0:
        print("\033[31mOpción inválida, seleccione un número del menu.\033[0m")
        continue

    # Inicio de sesion
    if accion_usuario == 1:
        print ("\nIntroduce tus datos")
        usuario_AN = pedir_texto("Introduce tu usuario por favor: ")
        contrasenya_AN = pedir_contrasenya("Introduce tu contraseña por favor: ")
        
        usuario_API= Usuario_Contrasenya(usuario_AN,contrasenya_AN)

        verif_u = verificar_usuario_correcta(usuario_API)
        verif_c = verificar_contrasenya_correcta(usuario_API)

        if verif_c == True and verif_u == True:
            print ("\n\033[36mBienvenid@ al recomendador de animes 2000\033[0m")
            accion_usuario = 0
            accion_usuario_anime = 1
            
        else:
            print ("\n\033[31mHubo algun problema con los datos o no estas registrad@.\033[0m\n")
    
    # Registro de usuario
    if accion_usuario == 2:
        accion_nombre_registro = input("Introduce tu nombre de usuario: ")
        indexErrors = 0
        verificacion_usuario = Usuario_Contrasenya(accion_nombre_registro,"123456")

        while (
            (accion_nombre_registro.isdigit() 
            or not accion_nombre_registro.strip().isalnum())
            and indexErrors < CANTIDAD_ERRORES
            or verificacion_usuario_existente(verificacion_usuario)
            ):
            indexErrors += 1
            accion_nombre_registro = input("\033[31mNombre no válido, elige uno nuevo: \033[0m")
            verificacion_usuario = Usuario_Contrasenya(accion_nombre_registro,"123456")
            if indexErrors >= CANTIDAD_ERRORES: break
        
        if indexErrors >= CANTIDAD_ERRORES: 
            print("\n\033[31mCantidad de errores alcanzados \033[0m\n")
            continue

        indexErrors = 0
        print("\n\033[32mLa contraseña debe tener:\n- Mínimo 8 caracteres\n- Una mayúscula\n- Un caracter especial\033[0m")
        accion_contrasenya_registro = input("Introduce la contraseña: ")

        while (not validar_password(accion_contrasenya_registro)) and indexErrors < CANTIDAD_ERRORES:
            indexErrors += 1
            print("\033[31mLa contraseña debe tener:\n- Mínimo 8 caracteres\n- Una mayúscula\n- Un caracter especial\033[0m")
            accion_contrasenya_registro = input("Introduce una nueva contraseña: ")
            if indexErrors >= CANTIDAD_ERRORES: break

        if indexErrors >= CANTIDAD_ERRORES: 
            print("\n\033[31mCantidad de errores alcanzados\033[0m\n")
            continue

        nuevo_usuario = Usuario_Contrasenya(accion_nombre_registro, accion_contrasenya_registro)
        DAO_logins.anyadir(nuevo_usuario)
        
        print(f"\n\033[32mNuevo usuario creado\033[0m")

        print ("\n\033[36mBienvenid@ al recomendador de animes 2000\033[0m")
        accion_usuario = 0
        accion_usuario_anime = 1

# Entrenar (solo la primera vez)
resp = req.post(f"{BASE_URL}/entrenar")

###     Seccion Recomendaciones
while accion_usuario_anime != 0 and DAO_logins!= None and DAO_logins.get_conexion() == True:
    print("\nOpciones:")
    print(mostrar_menu_acciones_animes())
    
    try:
        accion_usuario_anime = int(input(" Elige una opción: ").strip())
    except ValueError:
        print("\033[31mOpción inválida, escribe un número.\033[0m")
        continue

    if accion_usuario_anime > LARGO_OPCIONES_ANIME or accion_usuario_anime < 0:
        print("\033[31mOpción inválida, seleccione un número del menu.\033[0m")
        continue

    # Recomendar animes
    if accion_usuario_anime == 1:
        anime_entrante = ""
        calificacion_entrante = ""
        accion_usuario_recomendacion = 1

        while accion_usuario_recomendacion != 0 and DAO_logins.get_conexion() == True:
            print("\nOpciones:")
            print(mostrar_menu_acciones_recomendar())

            try:
                accion_usuario_recomendacion = int(input(" Elige una opción: ").strip())
            except ValueError:
                print("\033[31mOpción inválida, escribe un número.\033[0m")
                continue

            if accion_usuario_recomendacion > LARGO_OPCIONES_LOGIN or accion_usuario_recomendacion < 0:
                print("\033[31mOpción inválida, seleccione un número del menu.\033[0m")
                continue

            if accion_usuario_recomendacion == 1:
                print("\nAlgunas recomendaciones aleatorias")

                resp = req.get(f"{BASE_URL}/animes")
                animes = resp.json()["animes"]
                print(mostrar_lista_animes(animes))

                anime_entrante = pedir_anime("\nIntroduce el número/ID del anime: ")
                calificacion_entrante = pedir_calificacion("Introduce la calificación por favor (del 1 al 10): ")

                user_test_ratings[anime_entrante] = calificacion_entrante

                print(f"\n\033[32mCalificación de Anime agregada\033[0m")

            if accion_usuario_recomendacion == 2 and len(user_test_ratings) > 0:
                resp_recom = req.post(f"{BASE_URL}/recomendar", json=user_test_ratings)

                if resp_recom.status_code == 200:
                    data = resp_recom.json()
                    print(mostrar_lista_recomendaciones(data))
            
                else:
                    print("Error:", resp_recom.text)
                    
            if len(user_test_ratings) <= 0: print("\n\033[31mTu lista de calificados esta vacia\033[0m")

    # Entrenar otra vez
    if accion_usuario_anime == 2:
        resp = req.post(f"{BASE_URL}/entrenar?force=true")
        print(f"\n\033[32mEntrenamiento completado, modelo actualizado\033[0m")

    # Version
    if accion_usuario_anime == 3:
        resp = req.get(f"{BASE_URL}/version")
        data = resp.json()
        print(f"\n\033[32mVersion del codigo: {data['version']}\033[0m")

    # Testear
    if accion_usuario_anime == 4:
        resp = req.post(f"{BASE_URL}/recomendar", json=user_ratings_hardcore)

        if resp.status_code == 200:
            data = resp.json()
            print(mostrar_lista_recomendaciones(data))
            
        else:
            print("Error:", resp.text)

print("\n\033[36m Hazta luego...\n\033[0m")
DAO_logins.close()
clear(2)