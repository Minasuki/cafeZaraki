import React, { useEffect, useState } from 'react';

function Empleado() {
  const [orders, setOrders] = useState([]);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    // Conectar WebSocket
    const socket = new WebSocket("ws://localhost:8000/ws/employee");
    setWs(socket);

    socket.onopen = () => {
      console.log("Conectado al servidor de tiempo real");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "new_order") {
        setOrders(prev => [data.data, ...prev]); // Agregar al inicio
      }
    };

    socket.onerror = (error) => {
      console.error("Error WebSocket:", error);
    };

    return () => {
      socket.close();
    };
  }, []);

  // También cargar órdenes existentes al inicio (GET /orders)
  useEffect(() => {
    fetch("/api/orders")
      .then(res => res.json())
      .then(data => setOrders(data));
  }, []);

  return (
    <div>
      <h1>Panel del Empleado - Órdenes en tiempo real</h1>
      <ul>
        {orders.map(order => (
          <li key={order.id}>
            {order.customer_name} - Total: {order.total}
            <button>Preparar</button>
            <button>Cobrar</button>
          </li>
        ))}
      </ul>
    </div>
  );
}