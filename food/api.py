from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Dish, DishOrderItem, Order, Restaurant
from .serializers import DishSerializer, OrderCreateSerializer, RestaurantSerializer
from .services import schedule_order
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.core.handlers.wsgi import WSGIRequest
from rest_framework import status
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
import uuid
from rest_framework.routers import DefaultRouter


class FoodAPIViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [AllowAny]
 
    #HTTP GET/food/dishes
    @action(methods=["get"], detail=False)
    def dishes(self, request):
        dishes = Dish.objects.all()
        serializer = DishSerializer(dishes, many=True)
        return Response(data=serializer.data)
 
    #HTTP POST/food/orders
    @action(methods=["post"], detail=False, permission_classes=[IsAuthenticated])
    def orders(self, request: WSGIRequest):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
    
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                status="not_started",
                eta=serializer.validated_data["eta"]
            )
            
            for item in serializer.validated_data["food"]:
                DishOrderItem.objects.create(
                    order=order,
                    dish=item["dish"],  
                    quantity=item["quantity"],
                    restaurant=item["dish"].restaurant
                )
            schedule_order(order.id)
        return Response({"id": order.id, "eta": order.eta, "status": order.status}, status=status.HTTP_201_CREATED)

food_router = DefaultRouter()
food_router.register(r"food", FoodAPIViewSet, basename="food")
