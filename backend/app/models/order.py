# backend/app/models/order.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Modelo para los ítems que vienen en la solicitud
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float  # El precio al momento de la compra

# Modelo para la solicitud de creación de orden
class OrderCreate(BaseModel):
    customer_name: str
    items: List[OrderItemCreate]  # Lista de productos en el carrito

# Modelo para la respuesta (lo que devuelve la API)
class OrderResponse(BaseModel):
    id: int
    customer_name: str
    status: str
    total: float
    created_at: datetime
    items: Optional[List[OrderItemCreate]] = None  # Opcional para detalles