from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from backend.app.api.routes import products, orders  # Importamos orders

app = FastAPI(title="Café Zaraki API")

# Incluir routers
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])

# --- WebSocket para el panel del empleado ---
# Lista para mantener conexiones activas
active_connections = []

@app.websocket("/ws/employee")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Esperar mensajes del cliente (por si quieren confirmar algo)
            await websocket.receive_text()
            # No hacemos nada con los mensajes, solo mantenemos la conexión abierta
    except WebSocketDisconnect:
        active_connections.remove(websocket)

# Función para notificar a todos los empleados sobre una nueva orden
def notify_new_order(order_data: dict):
    for connection in active_connections:
        try:
            connection.send_json(order_data)
        except:
            # Si falla, eliminar la conexión (se manejará en el bucle principal)
            pass

# Endpoint de ejemplo para crear una orden (simulado)
@app.post("/api/v1/orders/create")
def create_order(customer_name: str, total: float):
    # Aquí insertas en la DB (usando tu get_connection)
    # ...
    # Después de guardar, notificas a los empleados
    order_data = {
        "id": 123,
        "customer_name": customer_name,
        "total": total,
        "status": "pending",
        "created_at": "2025-...",
    }
    notify_new_order(order_data)
    return {"message": "Orden creada y notificada"}

from app.api.routes import websocket

app.include_router(websocket.router)  

@app.get("/")
def root():
    return {"message": "Bienvenido a Café Zaraki"}