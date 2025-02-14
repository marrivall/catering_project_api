from django.db import models

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
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name} {self.price}  ({self.restaurant})"


class DishesOrder(models.Model):

    class Meta:
        db_table = "dishes_orders"
        verbose_name_plural = "dishes orders"

    external_order_id = models.CharField(max_length=255)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.pk} {self.external_order_id}"


class DishOrderItem(models.Model):

    class Meta:
        db_table = "dish_order_items"

    quantity = models.SmallIntegerField()

    order = models.ForeignKey("DishesOrder", on_delete=models.CASCADE)
    dish = models.ForeignKey("Dish", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"[{self.order.pk}] {self.dish.name}: {self.quantity}"
