from django.db import models
from django.conf import settings
from .enums import OrderStatus



class Restaurant(models.Model):
    class Meta:
        db_table = "restaurants"

    name = models.CharField(max_length=100, blank=False)
    address = models.CharField(max_length=100, blank=True)

    def __str__(self) -> str:
        return f"[{self.pk}] {self.name}"


class Dish(models.Model):
    class Meta:
        db_table = "dishes"
        verbose_name_plural = "dishes"

    name = models.CharField(max_length=50, null=True)
    price = models.IntegerField()
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE, related_name="dishes")

    def __str__(self) -> str:
        return f"{self.name} {self.price}  ({self.restaurant})"


class Order(models.Model):
    status = models.CharField(max_length=20)
    provider = models.CharField(max_length=20, null=True, blank=True)
    eta = models.DateField()
    external_id_bueno = models.CharField(max_length=200, null=True, blank=True)
    external_id_melange = models.CharField(max_length=200, null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, null=True, on_delete=models.CASCADE)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.pk} {self.status} for {self.user.email}"

    def __repr__(self) -> str:
        return super().__str__()


class DishOrderItem(models.Model):
    class Meta:
        db_table = "dish_order_items"

    quantity = models.SmallIntegerField()
    dish = models.ForeignKey("Dish", on_delete=models.CASCADE)
    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return f"[{self.order.pk}] {self.dish.name}: {self.quantity}"

class OrderProcessing(models.Model):
    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    external_id = models.CharField(max_length=200, unique=True, null=True, blank=True)
    external_id_bueno = models.CharField(max_length=200, null=True, blank=True)
    external_id_melange = models.CharField(max_length=200, null=True, blank=True)
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE) 
    status = models.CharField(max_length=50, default="not_started")

