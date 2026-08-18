# create_tables.py
import os
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def create_tables():
    """Crea las tablas necesarias para el e-commerce del café."""
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Habilitar extensión UUID (por si acaso)
        cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

        # 1. Tabla de productos (menú)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(100) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                category VARCHAR(50),
                image_url TEXT,
                is_available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        # 2. Tabla de órdenes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                customer_name VARCHAR(100) NOT NULL,
                customer_phone VARCHAR(20),
                status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'preparing', 'ready', 'paid')),
                total DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        # 3. Tabla de items de la orden
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
                product_id UUID REFERENCES products(id),
                quantity INT NOT NULL CHECK (quantity > 0),
                unit_price DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        # Confirmar los cambios
        conn.commit()
        print("✅ Tablas creadas exitosamente en la base de datos.")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error al crear las tablas: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    create_tables()