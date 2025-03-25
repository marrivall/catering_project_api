import uuid
import json 
import httpx 
from datetime import date, datetime, time
from time import sleep
from config import celery_app
from .enums import OrderStatus, Restaurant
from food.models import DishOrderItem, Order, OrderProcessing, Dish, Restaurant
import requests
from food.serializers import DishSerializer


def process_restaurant_order(order, restaurant, url):
    try:
        external_order = OrderProcessing.objects.get(order=order, restaurant=restaurant)
    except OrderProcessing.DoesNotExist:
        external_order = OrderProcessing.objects.create(
            order=order, 
            restaurant=restaurant,
            status='not_started'
        )    
        
    if not external_order.external_id:
        external_order.external_id = str(uuid.uuid4())
        external_order.save()
    
    payload = {"order": [], "id": external_order.external_id}
    for item in order.dishorderitem_set.all():
        dish_data = DishSerializer(item.dish).data
        dish_data["quantity"] =item.quantity
        payload["order"].append(dish_data)
    
    try:
        print(f"Send request to restaurant {restaurant} order: {order.id}")
        headers = {'Content-Type': 'application/json',}
        response = httpx.post(f"{url}/", json=payload, headers=headers)
        response.raise_for_status()
        api_response = response.json()
        print("API Response:", api_response)


        if "id" in api_response:
            external_id_from_api = api_response["id"]
            print(f"External_id {external_id_from_api} for order {order.id}")
            external_order.external_id = external_id_from_api
            external_order.save()
        
            if restaurant.name.lower() == 'melange':
                order.external_id_1 = external_id_from_api
                order.save()
            elif restaurant.name.lower() == 'bueno':
                order.external_id_2 = external_id_from_api
            order.save()
        else:
            print("API не повернув External ID! Відповідь API:", api_response)

    except httpx.RequestError as e:
        print(f"Request error: {e}")
        return
    except Exception as e:
        print(f"Error: {e}")
        return
    print("Payload for API:", json.dumps(payload, ensure_ascii=False, indent=4))

    response = httpx.get(f"{url}/{external_order.external_id}")
    response.raise_for_status()
            
    external_order.status = response.json()["status"]
    external_order.save()
    order.status = external_order.status
    order.save()
    print(f"Order status updated to {order.status}")

    print(f"Waiting 20 sec")
    sleep(20)
    print(f"Calling delivery service to pass the order")
 
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
    for item in order.dishorderitem_set.all():
        restaurant = item.dish.restaurant
        if restaurant.name.lower() == 'melange':
            # melange_order_processing.delay(order.id)
            melange_order_processing(order.id)
        elif restaurant.name.lower() == 'bueno':
            # bueno_order_processing.delay(order.id)
            bueno_order_processing(order.id)
        else:
            raise ValueError(f"Can not create order for {restaurant} restaurant")
 

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
