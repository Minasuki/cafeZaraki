from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

active_connections = []

@router.websocket("/ws/employee")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

def notify_new_order(order_data: dict):
    for conn in active_connections:
        try:
            conn.send_json(order_data)
        except:
            pass