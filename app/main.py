from fastapi import FastAPI, HTTPException, Depends, Request
from sqlmodel import Session, select
from typing import List
import mercadopago
import os
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv()
 
# Imports de modelos (tablas de BD)
from .models.product import Product
from .models.order import Order, OrderItem, OrderStatus
 
# Imports de schemas (request/response)
from .schemas.product import ProductCreate, ProductUpdate
from .schemas.order import OrderCreate, OrderResponse, OrderItemResponse
from .schemas.payment import PaymentResponse
 
# Imports de database
from .core.database import create_db_and_tables, get_session

app = FastAPI()



# Mercado Pago SDK
MERCADOPAGO_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
if not MERCADOPAGO_TOKEN:
    raise ValueError("❌ MERCADOPAGO_ACCESS_TOKEN no configurado en .env")
 
sdk = mercadopago.SDK(MERCADOPAGO_TOKEN)


FRONTEND_URL = os.getenv("FRONTEND_URL")



@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# ============================================
# ENDPOINT PARA SEED DE DATOS DE PRUEBA
# ============================================
 
@app.post("/seed")
async def seed_database(session: Session = Depends(get_session)):
    """Crear productos de prueba"""
    products = [
        Product(
            name="Laptop HP",
            description="Laptop HP 15.6 pulgadas, Intel i5, 8GB RAM",
            price=450000.00,
            stock=10,
            image_url="https://via.placeholder.com/300x300?text=Laptop"
        ),
        Product(
            name="Mouse Logitech",
            description="Mouse inalámbrico Logitech MX Master 3",
            price=25000.00,
            stock=50,
            image_url="https://via.placeholder.com/300x300?text=Mouse"
        ),
        Product(
            name="Teclado Mecánico",
            description="Teclado mecánico RGB con switches Cherry MX",
            price=35000.00,
            stock=30,
            image_url="https://via.placeholder.com/300x300?text=Teclado"
        ),
        Product(
            name="Monitor 24 pulgadas",
            description="Monitor Full HD 24 pulgadas, 144Hz",
            price=120000.00,
            stock=15,
            image_url="https://via.placeholder.com/300x300?text=Monitor"
        ),
        Product(
            name="Webcam HD",
            description="Webcam 1080p con micrófono incorporado",
            price=15000.00,
            stock=25,
            image_url="https://via.placeholder.com/300x300?text=Webcam"
        ),
    ]
    
    for product in products:
        session.add(product)
    
    session.commit()
    
    return {"message": f"Se crearon {len(products)} productos de prueba"}
 
@app.get("/products", response_model=List[Product])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Obtener todos los productos"""
    products = session.exec(select(Product).offset(skip).limit(limit)).all()
    return products

@app.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Obtener todas las órdenes"""
    orders = session.exec(select(Order).offset(skip).limit(limit)).all()
    
    # Construir respuesta con items
    orders_response = []
    for order in orders:
        items_response = []
        for item in order.items:
            items_response.append(OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.quantity * item.unit_price
            ))
        
        orders_response.append(OrderResponse(
            id=order.id,
            user_email=order.user_email,
            status=order.status,
            total_amount=order.total_amount,
            preference_id=order.preference_id,
            payment_id=order.payment_id,
            created_at=order.created_at,
            paid_at=order.paid_at,
            items=items_response
        ))
    
    return orders_response
 
 
@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, session: Session = Depends(get_session)):
    """Obtener una orden por ID"""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    # Construir respuesta con items
    items_response = []
    for item in order.items:
        items_response.append(OrderItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product.name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.quantity * item.unit_price
        ))
    
    return OrderResponse(
        id=order.id,
        user_email=order.user_email,
        status=order.status,
        total_amount=order.total_amount,
        preference_id=order.preference_id,
        payment_id=order.payment_id,
        created_at=order.created_at,
        paid_at=order.paid_at,
        items=items_response
    )
 
 
@app.post("/orders", response_model=PaymentResponse)
async def create_order(
    order_data: OrderCreate,
    session: Session = Depends(get_session)
):

    if not order_data.items:
        raise HTTPException(400, "La orden debe tener items")

    try:

        total_amount = 0
        items_for_mp = []

        order = Order(
            user_email=order_data.user_email,
            status=OrderStatus.PENDING,
            total_amount=0
        )

        session.add(order)

        for item in order_data.items:

            product = session.get(Product, item.product_id)

            if not product:
                raise HTTPException(404, f"Producto {item.product_id} no encontrado")

            if product.stock < item.quantity:
                raise HTTPException(
                    400,
                    f"Stock insuficiente para {product.name}"
                )

            subtotal = product.price * item.quantity
            total_amount += subtotal

            order_item = OrderItem(
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.price
            )

            order.items.append(order_item)

            items_for_mp.append({
                "title": product.name,
                "description": product.description or "",
                "quantity": item.quantity,
                "unit_price": product.price,
                "currency_id": "ARS"
            })

        order.total_amount = total_amount

        session.commit()
        session.refresh(order)

        preference_data = {
            "items": items_for_mp,
            "external_reference": str(order.id)
        }

        preference_response = sdk.preference().create(preference_data)

        preference = preference_response["response"]

        order.preference_id = preference["id"]

        session.add(order)
        session.commit()

        return PaymentResponse(
            order_id=order.id,
            preference_id=preference["id"],
            payment_url=preference["init_point"],
            sandbox_payment_url=preference.get("sandbox_init_point")
        )

    except Exception as e:
        session.rollback()
        raise HTTPException(500, str(e))