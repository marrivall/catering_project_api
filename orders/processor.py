from threading import Thread
from time import sleep
from datetime import date
from food.models import Order
from food.enums import OrderStatus
from shared.cache import CacheService
import redis

class Processor:

    EXCLUDE_STATUSES = (OrderStatus.DELIVERED, OrderStatus.NOT_DELIVERED,)

    def __init__(self):
        self._thread = Thread(target=self.process, daemon=True)
        self.today = date.today()
        self.cache_service = CacheService()
        self.namespace = "orders"
        self.key = "cached_orders"
        print(f"Orders Processor is created")


    def start(self):
        self._thread.start()
        print(f"Orders Processor started processing orders")


    def process(self):
        while True:
            self._process()
            sleep(15)
 

    def _process(self):
        cached_orders  = self.cache_service.get(self.namespace, self.key)   
        if not isinstance(cached_orders, dict):
            cached_orders = {} 

        if not cached_orders :  
            orders:  QuerySet[Order] = Order.objects.exclude(status__in=self.EXCLUDE_STATUSES)#дані з бд, якщо нема в кеші
            cached_orders = {}
            for order in orders:  
                cached_orders[order.id] = {"id": order.id, "status": order.status, "eta": order.eta}
            self.cache_service.set(self.namespace, self.key, cached_orders, ttl=None)
            print("Orders are cached in cache")
            return False
        else:
            print(f"Getting orders from cache {cached_orders}")

        orders_id = list(cached_orders.keys())
        changed_orders = Order.objects.filter(id__in=orders_id).exclude(status__in=self.EXCLUDE_STATUSES)
        if not changed_orders:  
            return False
        changes_applied = False
        updated_cache = cached_orders.copy()

        for order in changed_orders:
            cached_order = cached_orders.get(order.id, {})
            if order.status != cached_order.get("status"):
                updated_cache[order.id] = {"id": order.id, "status": order.status, "eta": order.eta}
                changes_applied = True

        if changes_applied:
            self.cache_service.set(self.namespace, self.key, updated_cache, ttl=None)
            print(f"Updated orders in cache {updated_cache}")
        return changes_applied

    def update_cache(self, order):
        cached_orders = self.cache_service.get(self.namespace, self.key)
        if order.id in cached_orders:
            cached_orders[order.id]["status"] = order.status
            self.cache_service.set(self.namespace, self.key, cached_orders, ttl=None)
        else:
            print(f"No order {order.id} in cache.")


    def _process_status(self, order):
            match order.status:
                case OrderStatus.NOT_STARTED:
                    self._process_not_started(order)
                    self.update_cache(order)
                case OrderStatus.COOKING_REJECTED:
                    self._process_cooking_rejected()
                    self.update_cache(order)
                case _:
                    print(f"Unrecognized order status: {order.status} passing")


    def _process_cooking_rejected(self):
         raise NotImplementedError


    def _process_not_started(self, order):
        if order.eta > self.today:
            return 
        elif order.eta < self.today:
            if order.status != OrderStatus.CANCELLED: 
                order.status = OrderStatus.CANCELLED
                order.save()
                print(f"Cancelled {order} order")
        else: 
            if order.status != OrderStatus.COOKING: 
                order.status = OrderStatus.COOKING
                order.save()

            restaurants  = set()
            for item in order.items.all():
                restaurants.add(item.dish.restaurants)
            print(f"Finished preparing order {order}, Resaurants: {restaurants}")


        
process = Processor()
process.start()










