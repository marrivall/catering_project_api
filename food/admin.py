from django.contrib import admin
from .models import Dish, Restaurant, DishesOrder, DishOrderItem

admin.site.register(Restaurant)


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "restaurant")
    search_fields = ("name", "price", "restaurant")
    list_filter = ("price" , "restaurant")


class DishOrderItemInline(admin.TabularInline):
    model = DishOrderItem
    fields = ("quantity", "dish", "order_external_id")

    def order_external_id(self, obj):
        return obj.order.external_order_id
    order_external_id.short_description = "External Order ID"
    

@admin.register(DishesOrder)
class DishesOrderAdmin(admin.ModelAdmin):
    inlines = (DishOrderItemInline,)
    list_display = ("external_order_id", "user")
    search_fields = ("external_order_id", "user__username")