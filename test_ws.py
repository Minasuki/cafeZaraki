import asyncio
import websockets
import json

async def listen():
    uri = "ws://localhost:8000/ws/employee"
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado al WebSocket del empleado. Esperando órdenes...")
            while True:
                mensaje = await websocket.recv()
                data = json.loads(mensaje)
                print("\n📦 Nueva orden recibida:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(listen())