# src/conexion.py
import mysql.connector

def conectar_bd():
    cnx = mysql.connector.connect(
        host="localhost",
        user="root",       
        password="piru412", 
        database="diagnostico_ia"
    )
    return cnx
