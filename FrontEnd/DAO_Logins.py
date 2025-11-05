import mysql.connector
from mysql.connector import Error
import bcrypt

class DAO_Logins:
    def __init__(self, db_user="root", db_password="", db_name="logins_api_anime", host="localhost"):
        self.__db_user = db_user
        self.__db_password = db_password
        self.__db_name = db_name
        self.__host = host
        self.__conexion = None
        self.__cursor = None
        self.__conexionHecha = False

    def conectar(self):
        """Intenta conectar con MySQL"""
        try:
            self.__conexion = mysql.connector.connect(
                host=self.__host,
                user=self.__db_user,
                password=self.__db_password,
                database=self.__db_name
            )
            self.__cursor = self.__conexion.cursor(dictionary=True)
            self.__conexionHecha = True
            print("✅ Conexión MySQL establecida correctamente.")
        except Error as e:
            print(f"❌ Error al conectar con MySQL: {e}")
            self.__conexionHecha = False

    def get_conexion(self):
        """Devuelve True si hay conexión activa"""
        return self.__conexionHecha

    def comprobar_usuario(self, login):
        """Comprueba si el usuario existe en la base de datos"""
        if not self.__conexionHecha:
            print("❌ No hay conexión activa con la base de datos.")
            return False
        try:
            sql = "SELECT usuario FROM usuario_contrasenyas WHERE usuario = %s"
            self.__cursor.execute(sql, (login.get_usuario(),))
            resultado = self.__cursor.fetchone()
            return resultado is not None
        except Error as e:
            print(f"❌ Error al comprobar usuario: {e}")
            return False

    def comprobar_login(self, login):
        """Valida usuario y contraseña usando bcrypt"""
        if not self.__conexionHecha:
            print("❌ No hay conexión activa con la base de datos.")
            return False
        try:
            sql = "SELECT contrasenya FROM usuario_contrasenyas WHERE usuario = %s"
            self.__cursor.execute(sql, (login.get_usuario(),))
            resultado = self.__cursor.fetchone()
            if not resultado:
                return False
            hash_guardado = resultado["contrasenya"]
            return bcrypt.checkpw(login.get_contrasenya().encode('utf-8'), hash_guardado.encode('utf-8'))
        except Error as e:
            print(f"❌ Error al comprobar login: {e}")
            return False

    def registrar_usuario(self, login):
        """Registra un nuevo usuario con contraseña hasheada"""
        if not self.__conexionHecha:
            print("❌ No hay conexión activa con la base de datos.")
            return False
        try:
            hash_contra = bcrypt.hashpw(login.get_contrasenya().encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            sql = "INSERT INTO usuario_contrasenyas (usuario, contrasenya) VALUES (%s, %s)"
            self.__cursor.execute(sql, (login.get_usuario(), hash_contra))
            self.__conexion.commit()
            print("✅ Usuario registrado correctamente.")
            return True
        except Error as e:
            print(f"❌ Error al registrar usuario: {e}")
            return False

    def ver_todos(self):
        """Devuelve todos los usuarios registrados"""
        if not self.__conexionHecha:
            return []
        self.__cursor.execute("SELECT * FROM usuario_contrasenyas")
        return self.__cursor.fetchall()

    def close(self):
        """Cierra la conexión"""
        if self.__conexionHecha:
            self.__cursor.close()
            self.__conexion.close()
            self.__conexionHecha = False
