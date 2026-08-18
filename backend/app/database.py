import os

import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener URL y validar que existe
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ La variable DATABASE_URL no está definida en el archivo .env")

def get_connection():
    """Retorna una conexión a PostgreSQL o None si falla."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión (verifica credenciales o que el servicio esté activo): {e}")
        return None
    except psycopg2.DatabaseError as e:
        print(f"❌ Error en la base de datos: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None