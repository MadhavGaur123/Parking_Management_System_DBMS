import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="madhav",
        database="dbms_project_final"
    )
