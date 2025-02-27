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
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView
from users.api import router as users_router
from food.api import food_router



urlpatterns =( [
    path("admin/", admin.site.urls),
    path("auth/token/", TokenObtainPairView.as_view()),
    path("api/food/", include(food_router.urls)),
    ]
    + users_router.urls
    + food_router.urls
)



# @dataclass
# class Dish():
#     id:int
#     name:int
#     price:int
#     restaurant: int

# storage = {
#     # "dishes": [Dish(id=1, name="salad", price = 200, restauran=1), Dish(id=2, name="fish",price = 250, restauran=2)],
#     # "basket": [BasketCreateRequestBody(id=1),],
#     # "basket_item": [BasketItem(id=1, basket_id=1, dish_id=1, quantity=1),]
# }

# @dataclass
# class Basket:
#     id: int

# @dataclass
# class BasketItem:
#     id: int

# def basket_create(request: WSGIRequest):
#     if request.method != "POST":
#         raise ValueError(f"method {request.method} is not allowed...")
#     else:
#         try:
#             last_basket: Basket = sorted(storage["baskets"], key= operator.attrgetter("id"))[-1]
#         except IndexError:
#             last_id  = 0
#         else:
#             last_id = last_basket.id
#     isinstance= Basket(id=last_basket +1)
#     storage["baskets"].append(isinstance)
#     print(storage["baskets"])
#     return JsonResponse({asdict(isinstance)})

    # path("import-dishes/", import_dishes),
    # path("users/", user_create_retrieve),  # GET to retrieve user, POST to create user
    # path(
    #     "users/<id:int>", user_update_delete
    # ),  # PUT to updaste user, DELETE to remove user
    # path("users/password/forgot", password_forgot),  # POST to generate temp UUID key
    # path(
    #     "users/passwordt/change", password_change
    # ),  # POST, receive key and new password
    # AUTH
    # ==================
    # path("auth/token", access_token),  # POST
    # BASKET & ORDERS
    # ==================
    # path("basket/", basket_create),  # POST  -> return ID
    # path("basket/<id:int>", basket_retrieve),  # GET to see all details
    # path(
    #     "basket/<id:int>/dishes/<id:int>", basket_dish_add_update_delete
    # ),  # PUT (change quantity), DELETE, POST (add dish)
    # path("basket/<id:int>/order", order_from_basket),  # POST -> [Order] with ID
    # path(
    #     "orders/<id:int>", order_details
    # ),  # GET (owner, support), PUT (only by SUPPORT)