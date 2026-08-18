# seed_data.py
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def insert_products():
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Lista de productos de ejemplo
        products = [
            ("Café Americano", "Café filtrado, intenso y aromático.", 2.50, "Bebidas"),
            ("Café Latte", "Café con leche cremosa.", 3.00, "Bebidas"),
            ("Café Mocha", "Café con chocolate y leche.", 3.50, "Bebidas"),
            ("Capuchino", "Café con espuma de leche.", 3.20, "Bebidas"),
            ("Té Verde", "Té verde japonés.", 2.00, "Bebidas"),
            ("Croissant", "Croissant de mantequilla.", 2.80, "Pasteles"),
            ("Muffin de Arándanos", "Muffin esponjoso con arándanos.", 3.00, "Pasteles"),
            ("Brownie", "Brownie de chocolate con nueces.", 3.50, "Pasteles")
        ]

        for name, description, price, category in products:
            cursor.execute("""
                INSERT INTO products (name, description, price, category)
                VALUES (%s, %s, %s, %s)
            """, (name, description, price, category))

        conn.commit()
        print(f"✅ Se insertaron {len(products)} productos de ejemplo.")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error al insertar productos: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    insert_products()