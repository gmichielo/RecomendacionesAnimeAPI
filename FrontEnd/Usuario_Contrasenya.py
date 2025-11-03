class Usuario_Contrasenya():

    def __init__(self, usuario, contrasenya):
        self.__usuario = usuario
        self.__contrasenya = contrasenya

    def get_usuario(self):
        return self.__usuario
    
    def set_usuario(self, usuario):
        self.__usuario = usuario

    def get_contrasenya(self):
        return self.__contrasenya

    def set_usuario(self, contrasenya):
        self.__contrasenya = contrasenya

    def __str__(self):
        return f"Usuario: {self.__usuario} | Contraseña: {self.__contrasenya}"