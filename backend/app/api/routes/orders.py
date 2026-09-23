# backend/app/api/routes/orders.py
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from backend.app.database import get_connection
from backend.app.models.order import OrderCreate, OrderResponse
from backend.app.api.routes.websocket import notify_new_order
from pydantic import BaseModel
import asyncio
from backend.app.api.routes.websocket import notify_new_order

# Importamos la función de notificación WebSocket (la crearemos después)
# from backend.app.api.routes.websocket import notify_new_order

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(order_data: OrderCreate):

    conn = get_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Error de conexión a la base de datos"
        )

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
            (order_data.customer_name, total),
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
                (order_id, item.product_id, item.quantity, item.unit_price),
            )

        # 4. Confirmar la transacción (commit)
        conn.commit()

        # 5. (Opcional) Notificar a los empleados por WebSocket
        asyncio.create_task(notify_new_order (
            {
                "id": order_id,
                "customer_name": order_data.customer_name,
                "total": float(total),
                "status": "pending",
                "created_at": created_at.isoformat(),
            }
        ))

        # 6. Devolver la respuesta
        return OrderResponse(
            id=order_id,
            customer_name=order_data.customer_name,
            status="pending",
            total=total,
            created_at=created_at,
        )

    except Exception as e:
        # Si algo falla, revertimos todos los cambios (rollback)
        conn.rollback()
        print(f"❌ Error al crear la orden: {e}")
        raise HTTPException(
            status_code=400, detail=f"Error al procesar la orden: {str(e)}"
        )

    finally:
        cursor.close()
        conn.close()


@router.get("/", response_model=list[OrderResponse])
def get_orders(
    status: Optional[str] = Query(
        None, description="Filtrar por estado: pending, preparing, ready, paid"
    ),
):

    conn = get_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Error de conexión a la base de datos"
        )

    cursor = conn.cursor()
    try:
        if status:
            cursor.execute(
                """
                SELECT id, customer_name, status, total, created_at
                FROM orders
                WHERE status = %s
                ORDER BY created_at ASC
                """,
                (status,),
            )
        else:
            cursor.execute("""
                SELECT id, customer_name, status, total, created_at
                FROM orders
                ORDER BY created_at ASC
                """)

        rows = cursor.fetchall()

        return [
            {
                "id": r[0],
                "customer_name": r[1],
                "status": r[2],
                "total": float(r[3]),
                "created_at": r[4],
            }
            for r in rows
        ]
    except Exception as e:
        print(f"❌ Error al obtener órdenes: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al obtener órdenes: {str(e)}"
        )
    finally:
        cursor.close()
        conn.close()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_detail(order_id: int):
    """
    Devuelve el detalle completo de una orden, incluyendo sus ítems y el nombre del producto.
    """
    conn = get_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Error de conexión a la base de datos"
        )

    cursor = conn.cursor()
    try:
        # 1. Obtener la orden principal
        cursor.execute(
            """
            SELECT id, customer_name, status, total, created_at
            FROM orders
            WHERE id = %s
            """,
            (order_id,),
        )
        order_row = cursor.fetchone()

        if not order_row:
            raise HTTPException(
                status_code=404, detail=f"Orden con id {order_id} no encontrada"
            )

        # 2. Obtener los ítems de la orden con el nombre del producto
        cursor.execute(
            """
            SELECT oi.id, oi.product_id, oi.quantity, oi.unit_price, p.name
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
            """,
            (order_id,),
        )
        items_rows = cursor.fetchall()

        items = [
            {
                "id": r[0],
                "product_id": r[1],
                "quantity": r[2],
                "unit_price": float(r[3]),
                "product_name": r[4],
            }
            for r in items_rows
        ]

        return {
            "id": order_row[0],
            "customer_name": order_row[1],
            "status": order_row[2],
            "total": float(order_row[3]),
            "created_at": order_row[4],
            "items": items,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error al obtener detalle de la orden: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al obtener la orden: {str(e)}"
        )
    finally:
        cursor.close()
        conn.close()


class StatusUpdate(BaseModel):
    status: str


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: int, update: StatusUpdate):
    """
    Actualiza el estado de una orden.
    Estados válidos: pending, preparing, ready, paid.
    """
    valid_statuses = {"pending", "preparing", "ready", "paid"}
    if update.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido. Debe ser uno de: {', '.join(valid_statuses)}",
        )

    conn = get_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Error de conexión a la base de datos"
        )

    cursor = conn.cursor()
    try:
        # Verificar que la orden existe
        cursor.execute("SELECT id FROM orders WHERE id = %s", (order_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404, detail=f"Orden {order_id} no encontrada"
            )

        # Actualizar el estado
        cursor.execute(
            """
            UPDATE orders
            SET status = %s
            WHERE id = %s
            RETURNING id, customer_name, status, total, created_at
            """,
            (update.status, order_id),
        )
        row = cursor.fetchone()
        conn.commit()

        return {
            "id": row[0],
            "customer_name": row[1],
            "status": row[2],
            "total": float(row[3]),
            "created_at": row[4],
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al actualizar estado: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al actualizar estado: {str(e)}"
        )
    finally:
        cursor.close()
        conn.close()
