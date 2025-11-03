import mysql.connector
from mysql.connector import Error
import bcrypt

class DAO_Logins():
    def __init__(self, user_input: str, password_input: str):

        self.__host = "localhost"
        self.__user = user_input
        self.__password = password_input
        self.__database = "logins_api_anime"
        self.__conexionHecha = False
        
    def get_conexion(self):
        return self.__conexionHecha
    
    def conectar(self):
        try:
            self.__mydb = mysql.connector.connect(
                host=self.__host,
                user=self.__user,
                password=self.__password,
                database=self.__database
            )
            self.connected = self.__mydb.is_connected()
            self.__mycursor = self.__mydb.cursor()
            self.__conexionHecha = True

        except Error as err:
            self.__mydb = None
            self.__mydb = False
            self.last_error = err

    def close(self):
        if self.__mydb and self.__mydb.is_connected():
            self.__mycursor.close()
            self.__mydb.close()
            self.__conexionHecha = False

    def reconectar(self, user=None, password=None):
        if user:
            self.__user = user
        if password:
            self.__password = password
        self.conectar()
        return self.connected
    
    def comprobar_login(self, login):
        try:
            sql = "SELECT contrasenya FROM usuario_contrasenyas WHERE usuario = %s"
            val = (login.get_usuario(), )
            self.__mycursor.execute(sql, val)
            resultado = self.__mycursor.fetchone()

            if not resultado:
                return False
            
            # Recuperar el hash almacenado
            password_hash = resultado[0]

            # Comparar la contraseña ingresada con el hash almacenado
            return bcrypt.checkpw(login.get_contrasenya().encode(), password_hash.encode())

        except Error as err:
            print(f"Error al comprobar login: {err}")
            return False
        
    def comprobar_usuario(self, login):
        try:
            sql = "SELECT usuario FROM usuario_contrasenyas WHERE usuario = %s"
            val = (login.get_usuario(), )
            self.__mycursor.execute(sql, val)
            resultado = self.__mycursor.fetchone()

            # Si hay un resultado, el usuario existe
            return resultado is not None

        except Error as err:
            print(f"Error al comprobar usuario: {err}")
            return False

    def anyadir(self, login):
        password_hash = bcrypt.hashpw(login.get_contrasenya().encode(), bcrypt.gensalt()).decode()
        sql = "INSERT INTO usuario_contrasenyas (usuario, contrasenya) VALUES (%s, %s)"
        val = (login.get_usuario(), password_hash)
        self.__mycursor.execute(sql, val)
        self.__mydb.commit()

    def ver(self):
        self.__mycursor.execute("SELECT * FROM usuario_contrasenyas")
        return self.__mycursor.fetchall()
    
    def actualizarContrasenya(self, login):
        password_hash = bcrypt.hashpw(login.get_contrasenya().encode(), bcrypt.gensalt()).decode()
        sql = "UPDATE usuario_contrasenyas SET contrasenya = %s WHERE usuario = %s"
        valores = (password_hash, login.get_usuario())
        self.__mycursor.execute(sql, valores)
        self.__mydb.commit()

    def actualizarUsuario(self, user_nuevo, login):
        sql = "UPDATE usuario_contrasenyas SET usuario = %s WHERE usuario = %s"
        valores = (user_nuevo, login.get_usuario())
        self.__mycursor.execute(sql, valores)
        self.__mydb.commit()

    def __str__(self):
        return "DAO de Logins"
