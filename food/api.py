from django.core.handlers.wsgi import WSGIRequest
from rest_framework import status, viewsets, routers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Dish, DishOrderItem, Order, Restaurant
from .serializers import DishSerializer, OrderSerializer, RestaurantSerializer
from .enums import OrderStatus


class FoodAPIViewSet(viewsets.GenericViewSet):
    #HTTP GET/food/dishes
    @action(methods=["get"], detail=False)
    def dishes(self, request):
        dishes = Dish.objects.all()
        serializer = DishSerializer(dishes, many=True)

        return Response(data=serializer.data)

    #HTTP POST/food/orders
    @action(methods=["post"], detail=False)
    def orders(self, request: WSGIRequest):


        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not isinstance(serializer.validated_data, dict):
            raise ValueError(...)

        order = Order.objects.create(status=OrderStatus.NOT_STARTED, user=request.user)
        print(f"New Food Order is created: {order.pk}")

        try:
            dishes_order = serializer.validated_data["food"]
        except KeyError as error:
            raise ValueError("Food order is not properly built")

        for dish_order in dishes_order:
            instance = DishOrderItem.objects.create(
                dish=dish_order["dish"], quantity=dish_order["quantity"], order=order
            )
            print(f"New Dish Order Item is created: {instance.pk}")

        return Response(
            data = serializer.data,
            status=status.HTTP_201_CREATED,
        )


#---------------------------------------------------------------
#Restaurants 
#---------------------------------------------------------------

class RestaurantAPIViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.AllowAny]

#HTTP GET/restaurants
    def list(self, request):
        restaurants = self.get_queryset()
        serializer = self.get_serializer(restaurants, many=True)
        return Response(data=serializer.data)

#HTTP POST /restaurants
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        restaurant = serializer.save()
        return Response(
            data = serializer.data,
            status=status.HTTP_201_CREATED,
        )
    
#HTTP GET /restaurants/ID
    def retrieve(self, request, pk=None):
        restaurant = Restaurant.objects.get(pk=pk)
        serializer = self.get_serializer(restaurant)
        return Response(data = serializer.data, status=status.HTTP_200_OK)
    
    #get certain resntaurant's dishes
    @action(detail=True, methods=['get'])
    def dishes(self, request, pk=None):
        restaurant = Restaurant.objects.get(pk=pk)
        dishes = restaurant.dishes.all()
        serializer = DishSerializer(dishes, many=True)
        return Response(serializer.data)
        

food_router = routers.DefaultRouter()
food_router.register(r"food", FoodAPIViewSet, basename="food")
food_router.register(r"restaurants", RestaurantAPIViewSet, basename="restaurants")
