from rest_framework import serializers
from .models import Dish, Restaurant, Order, DishOrderItem


class DishSerializer(serializers.ModelSerializer):
    restaurant = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all())
    class Meta:
        model = Dish
        fields = "__all__"

class RestaurantSerializer(serializers.ModelSerializer):
    dishes = DishSerializer(many=True, read_only=True)
    class Meta:
        model = Restaurant
        fields = "__all__"



class DishOrderSerializer(serializers.Serializer):
    dish = serializers.PrimaryKeyRelatedField(queryset=Dish.objects.all())
    quantity = serializers.IntegerField(min_value=1, max_value=20)


class OrderCreateSerializer(serializers.Serializer):
    food = DishOrderSerializer(many=True)
    eta = serializers.DateField()
    total = serializers.IntegerField(min_value=1, read_only=True)



