import uuid
import json 
import httpx 
from datetime import date, datetime, time
from time import sleep
from config import celery_app
from .enums import OrderStatus, Restaurant
from food.models import DishOrderItem, Order, OrderProcessing, Dish, Restaurant
from food.serializers import DishSerializer


def process_restaurant_order(order, restaurant, url):
    
    external_order = OrderProcessing.objects.filter(order=order, restaurant=restaurant).first()
    
    if external_order and external_order.status != 'not_started':
        print(f"Order {order.id} already processed for restaurant {restaurant.name}")
        return None

    if not external_order:
        external_order = OrderProcessing.objects.create(
            order=order, 
            restaurant=restaurant,
            status='not_started'
        ) 
    
    payload = {
        "order": [
            {
                "dish": str(item.dish.id),
                "quantity": item.quantity
            } for item in order.dishorderitem_set.all()
        ],
        "eta": order.eta.isoformat(),
    }
    
    try:
        print(f"Send request to restaurant {restaurant} order: {order.id}")
        headers = {'Content-Type': 'application/json'}
        
        if restaurant.name.lower() == 'bueno':
            response = httpx.post("http://localhost:8002/api/orders/", json=payload, headers=headers)
        elif restaurant.name.lower() == 'melange':
            response = httpx.post("http://localhost:8001/api/orders/", json=payload, headers=headers, follow_redirects=True)
        else:
            raise ValueError(f"No restaurant: {restaurant}")

        response.raise_for_status()
        api_response = response.json()
        print("API Response:", api_response)

        external_id_from_api = api_response.get("id")
        if external_id_from_api:
            external_order.external_id = external_id_from_api
            external_order.status = 'cooking' 
            external_order.save()
        
            if restaurant.name.lower() == 'melange':
                order.external_id_melange = external_id_from_api
            elif restaurant.name.lower() == 'bueno':
                order.external_id_bueno = external_id_from_api
            order.save()
        else:
            print("No External ID!")
        print(f"external id for order {order.id}, restaurant: {restaurant.name}: {external_id_from_api}")
        return api_response

    except httpx.RequestError as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        external_order.status = 'failed'
        external_order.save()

    return None
 
# @celery_app.task
def melange_order_processing(order_id):
    order = Order.objects.get(id=order_id)
    restaurant = Restaurant.objects.get(name__iexact='melange')
    process_restaurant_order(order, restaurant, "http://localhost:8001/api/orders")

# @celery_app.task
def bueno_order_processing(order_id):
    order = Order.objects.get(id=order_id)
    restaurant = Restaurant.objects.get(name__iexact='bueno')
    process_restaurant_order(order, restaurant, "http://localhost:8002/api/orders")
 
# @celery_app.task
def _schedule_order(order_id):
    order = Order.objects.get(id=order_id)
    processed_restaurants = set()

    for item in order.dishorderitem_set.all():
        restaurant = item.dish.restaurant
        
        if restaurant.name.lower() in processed_restaurants:
            continue

 
        if restaurant.name.lower() == 'melange':
            # melange_order_processing.delay(order.id)
            melange_order_processing(order.id)
        elif restaurant.name.lower() == 'bueno':
            # bueno_order_processing.delay(order.id)
            bueno_order_processing(order.id)
        else:
            raise ValueError(f"Can not create order for {restaurant} restaurant")
        processed_restaurants.add(restaurant.name.lower())
 

# @celery_app.task
def schedule_order(order_id):
    order = Order.objects.get(id=order_id) 
    assert type(order.eta) is date
 
    today = date.today()
    
    if order.eta <= today:  
        print(f"The order will be started processing now")
        _schedule_order(order.id)
    else:
        eta = datetime.combine(order.eta, time(hour=3))
        print(f"The order will be scheduled for {eta}")
        # schedule_order.apply_async(args=[order_id], eta=eta)
        _schedule_order(order.id)
