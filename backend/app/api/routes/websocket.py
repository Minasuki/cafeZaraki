# backend/app/api/routes/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter()

# Lista global de conexiones activas (los empleados conectados)
active_connections: List[WebSocket] = []


@router.websocket("/ws/employee")
async def websocket_employee(websocket: WebSocket):
    """
    Endpoint WebSocket para el panel del empleado.
    El empleado se conecta aquí y recibe notificaciones de nuevas órdenes.
    """
    await websocket.accept()
    active_connections.append(websocket)
    print(f"✅ Empleado conectado. Total conexiones: {len(active_connections)}")
    
    try:
        while True:
            # Mantener la conexión viva esperando mensajes (aunque no hacemos nada con ellos)
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"❌ Empleado desconectado. Total conexiones: {len(active_connections)}")


async def notify_new_order(order_data: dict):
    """
    Notifica a todos los empleados conectados sobre una nueva orden.
    Se llama desde el endpoint POST /orders.
    """
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(order_data)
        except Exception as e:
            print(f"⚠️ Error al enviar a un cliente: {e}")
            disconnected.append(connection)
    
    # Limpiar conexiones muertas
    for conn in disconnected:
        if conn in active_connections:
            active_connections.remove(conn)