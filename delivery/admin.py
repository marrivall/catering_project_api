from django.contrib import admin
from .models import DeliveryDishesOrder

@admin.register(DeliveryDishesOrder)
class DeliveryDishesOrderAdmin(admin.ModelAdmin):
    list_display = ("external_order_id", "status", "provider", "addresses")
    search_fields = ("external_order_id", "provider", "status")
    list_filter = ("provider", "status")



