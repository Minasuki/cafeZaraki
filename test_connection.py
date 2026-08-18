# test_connection.py (Síncrono)
from database import get_connection

def main():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Conectado exitosamente a: {version[0]}")
        cursor.close()
        conn.close()
    else:
        print("❌ No se pudo conectar.")

if __name__ == "__main__":
    main()