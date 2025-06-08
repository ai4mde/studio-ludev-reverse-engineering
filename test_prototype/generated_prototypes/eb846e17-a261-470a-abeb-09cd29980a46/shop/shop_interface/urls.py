from django.urls import path
from . import views

urlpatterns = [
    path("", views.homerender, name="shop_interface-homerender"),
    ]