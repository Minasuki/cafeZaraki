from fastapi import APIRouter, HTTPException
from backend.app.database import get_connection
from backend.app.models.product import ProductResponse


router = APIRouter()

@router.get("/", response_model=list[ProductResponse])
def get_products():
    conn = get_connection()
    if not conn:
        raise HTTPException(500, "Error de base de datos")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price, category, is_available FROM products")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "id": r[0],
            "name": r[1],
            "description": r[2],
            "price": float(r[3]),
            "category": r[4],
            "is_available": r[5]
        }
        for r in rows
    ]