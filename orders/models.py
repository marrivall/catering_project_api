from django.db import models
from restaurants.models import Dish
from users.models import User

class Order(models.Model):
    external_order_id = models.CharField(max_length=255)

    user = models.ForeignKey(User, on_delete=models.CASCADE)


class DishOrder(models.Model):

    quantity = models.SmallIntegerField()

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)

class DeliveryOrder(models.Model):
    provider = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    addresses = models.TextField()
    external_order_id = models.CharField(max_length=255)

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
