from django.core.handlers.wsgi import WSGIRequest
from rest_framework import status, viewsets, routers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Dish, DishOrderItem, Order, Restaurant
from .serializers import DishSerializer, OrderCreateSerializer, RestaurantSerializer
from .enums import OrderStatus
from rest_framework.generics import get_object_or_404
from orders.processor import Processor



class FoodAPIViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [permissions.AllowAny]

    #HTTP GET/food/dishes
    @action(methods=["get"], detail=False)
    def dishes(self, request):
        dishes = Dish.objects.all()
        serializer = DishSerializer(dishes, many=True)

        return Response(data=serializer.data)

    #HTTP POST/food/orders
    @action(methods=["post"], detail=False)
    def orders(self, request: WSGIRequest):


        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not isinstance(serializer.validated_data, dict):
            raise ValueError(...)

        order = Order.objects.create(
            status=OrderStatus.NOT_STARTED, user=request.user, eta=serializer.validated_data["eta"]
            )
        print(f"New Food Order is created: {order.pk}\nETA: {order.eta}")

        try:
            dishes_order = serializer.validated_data["food"]
        except KeyError as error:
            raise ValueError("Food order is not properly built")

        for dish_order in dishes_order:
            instance = DishOrderItem.objects.create(
                dish=dish_order["dish"], quantity=dish_order["quantity"], order=order
            )
            print(f"New Dish Order Item is created: {instance.pk}")

        cache_service = CacheService()
        cached_orders = cache_service.get("orders", "cached_orders") 
        cached_orders[order.id] = {"id": order.id, "status": order.status, "eta": str(order.eta)}
        cache_service.set("orders", "cached_orders", cached_orders, ttl=None)


        return Response(data={
                "id": order.pk,
                "status": order.status,
                "eta": order.eta,
                "total": 9999,
            },
            status=status.HTTP_201_CREATED,
            )


#---------------------------------------------------------------
#Restaurants 
#---------------------------------------------------------------

    @action(methods=["get"], detail=False)
    def restaurants(self, request):
        restaurants = Restaurant.objects.all()
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(data=serializer.data)
    
    # HTTP POST /food/restaurants/
    @action(methods=["post"], detail=False)
    def create_restaurant(self, request):
        serializer = RestaurantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        restaurant = serializer.save()
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED,
        )
    
    # HTTP GET /food/restaurants/{pk}/
    @action(methods=["get"], detail=False, url_path='restaurants/(?P<restaurant_pk>[^/.]+)')
    def retrieve_restaurant(self, request, restaurant_pk=None):
        restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
        serializer = RestaurantSerializer(restaurant)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    # HTTP GET /food/restaurants/{pk}/dishes/
    @action(methods=["get"], detail=True, url_path='restaurants/(?P<restaurant_pk>[^/.]+)/dishes')
    def restaurant_dishes(self, request, restaurant_pk=None):
        restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
        dishes = restaurant.dishes.all()
        serializer = DishSerializer(dishes, many=True)
        return Response(serializer.data)
        

food_router = routers.DefaultRouter()
food_router.register(r"food", FoodAPIViewSet, basename="food")
