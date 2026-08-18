from fastapi import APIRouter, HTTPException
from app.core.database import get_connection
from app.models.order import OrderCreate, OrderResponse

router = APIRouter()

@router.get("/", response_model=list[OrderResponse])
def get_orders():
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de conexión a DB")
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_name, status, total, created_at FROM orders ORDER BY created_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"id": r[0], "customer_name": r[1], "status": r[2], "total": r[3], "created_at": r[4]} for r in rows]

@router.post("/", response_model=OrderResponse)
def create_order(order: OrderCreate):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de conexión a DB")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (customer_name, total, status) VALUES (%s, %s, 'pending') RETURNING id, customer_name, status, total, created_at",
        (order.customer_name, order.total)
    )
    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return {"id": row[0], "customer_name": row[1], "status": row[2], "total": row[3], "created_at": row[4]}