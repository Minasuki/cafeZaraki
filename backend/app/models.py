from fastapi import FastAPI
from app.api.routes import orders

app = FastAPI(title="Café Zaraki API")

app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])

@app.get("/")
def root():
    return {"message": "Bienvenido a Café Zaraki"}