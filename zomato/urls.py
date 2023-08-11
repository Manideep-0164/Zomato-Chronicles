from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("menu/", views.menu, name="menu"),
    path("dishform/", views.add_dish, name="add_dish"),
    path("removedish/<int:dish_id>/", views.delete_dish, name="delete_dish"),
    path("updatedish/<int:dish_id>/", views.update_dish, name="update_dish"),
    path("processorder/", views.process_order, name="process_order"),
    path("orderslist/", views.orders_list, name="orders_list"),
    path("updatestatus/<int:order_id>/", views.update_status, name="update_status"),
]