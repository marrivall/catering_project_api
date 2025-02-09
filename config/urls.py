"""
URL configuration for config project.
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from users.models import User 
from restaurants.models import Restaurant, Dish
from orders.models import Order, DishOrder, DeliveryOrder
from rest_framework import routers, serializers, viewsets

#--------------------------------------------------------------------------------------
# USERS
#--------------------------------------------------------------------------------------
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'address', 'phone']

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

#--------------------------------------------------------------------------------------
# RESTAURANT
#--------------------------------------------------------------------------------------
class RestaurantSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['name', 'address']

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
#--------------------------------------------------------------------------------------
# DISH
#--------------------------------------------------------------------------------------
class DishSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dish
        fields = ['name', 'restaurant']

class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer

#--------------------------------------------------------------------------------------
# ORDER
#--------------------------------------------------------------------------------------
class OrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Order
        fields = ['external_order_id', 'user']

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

#--------------------------------------------------------------------------------------
# DishOrder
#--------------------------------------------------------------------------------------
class DishOrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DishOrder
        fields = ['quantity', 'order', 'dish']

class DishOrderViewSet(viewsets.ModelViewSet):
    queryset = DishOrder.objects.all()
    serializer_class =DishOrderSerializer

#--------------------------------------------------------------------------------------
# DeliveryOrder
#--------------------------------------------------------------------------------------
class DeliveryOrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DeliveryOrder
        fields = ['provider', 'status', 'addresses', 'external_order_id', 'order']

class DeliveryOrderViewSet(viewsets.ModelViewSet):
    queryset = DeliveryOrder.objects.all()
    serializer_class = DeliveryOrderSerializer


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'restaurants', RestaurantViewSet)
router.register(r'dishes', DishViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'dishorders', DishOrderViewSet)
router.register(r'deliveryorders', DeliveryOrderViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
]
