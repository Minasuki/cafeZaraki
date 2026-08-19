# backend/app/api/routes/orders.py
from fastapi import APIRouter, HTTPException
from backend.app.database import get_connection
from backend.app.models.order import OrderCreate, OrderResponse
from datetime import datetime

# Importamos la función de notificación WebSocket (la crearemos después)
# from backend.app.api.routes.websocket import notify_new_order

router = APIRouter()

@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(order_data: OrderCreate):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    cursor = conn.cursor()
    try:
        # 1. Calcular el total de la orden a partir de los ítems enviados
        total = sum(item.unit_price * item.quantity for item in order_data.items)
        
        # 2. Insertar la orden en la tabla `orders`
        cursor.execute(
            """
            INSERT INTO orders (customer_name, total, status)
            VALUES (%s, %s, 'pending')
            RETURNING id, created_at
            """,
            (order_data.customer_name, total)
        )
        order_row = cursor.fetchone()
        order_id = order_row[0]
        created_at = order_row[1]
        
        # 3. Insertar los ítems de la orden en la tabla `order_items`
        for item in order_data.items:
            cursor.execute(
                """
                INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
                """,
                (order_id, item.product_id, item.quantity, item.unit_price)
            )
        
        # 4. Confirmar la transacción (commit)
        conn.commit()
        
        # 5. (Opcional) Notificar a los empleados por WebSocket
        # notify_new_order({
        #     "id": order_id,
        #     "customer_name": order_data.customer_name,
        #     "total": total,
        #     "status": "pending",
        #     "created_at": created_at.isoformat()
        # })
        
        # 6. Devolver la respuesta
        return OrderResponse(
            id=order_id,
            customer_name=order_data.customer_name,
            status="pending",
            total=total,
            created_at=created_at
        )
    
    except Exception as e:
        # Si algo falla, revertimos todos los cambios (rollback)
        conn.rollback()
        print(f"❌ Error al crear la orden: {e}")
        raise HTTPException(status_code=400, detail=f"Error al procesar la orden: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()