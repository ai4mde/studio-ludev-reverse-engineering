from django.urls import path
from . import views

urlpatterns = [
    path("", views.homerender, name="user-homerender"),
    path("render_user_shopping_cart", views.render_user_shopping_cart, name="render_user_shopping_cart"),
    
    path('shopping_cart_customer_cart_get_num_of_items/<int:instance_id>', views.shopping_cart_customer_cart_get_num_of_items, name='shopping_cart_customer_cart_get_num_of_items'),
    path("render_user_profile", views.render_user_profile, name="render_user_profile"),
    path('profile_customer_profile_create/', views.profile_customer_profile_create, name='profile_customer_profile_create'),
    path('profile_customer_profile_create_popup/', views.profile_customer_profile_create_popup, name='profile_customer_profile_create_popup'),
    path('profile_customer_profile_update/<int:instance_id>/', views.profile_customer_profile_update, name='profile_customer_profile_update'),
    path('profile_customer_profile_update_popup/<int:instance_id>/', views.profile_customer_profile_update_popup, name='profile_customer_profile_update_popup'),
    path('profile_customer_profile_delete/<int:instance_id>/', views.profile_customer_profile_delete, name='profile_customer_profile_delete'),
    
    path('profile_customer_profile_get_name/<int:instance_id>', views.profile_customer_profile_get_name, name='profile_customer_profile_get_name'),
    
    path('profile_customer_profile_set_name/<int:instance_id>', views.profile_customer_profile_set_name, name='profile_customer_profile_set_name'),
    
    path('profile_customer_profile_set_has_membership/<int:instance_id>', views.profile_customer_profile_set_has_membership, name='profile_customer_profile_set_has_membership'),
    
    path('profile_customer_profile_get_has_membership/<int:instance_id>', views.profile_customer_profile_get_has_membership, name='profile_customer_profile_get_has_membership'),
    
    path('profile_customer_profile_get_customer_email/<int:instance_id>', views.profile_customer_profile_get_customer_email, name='profile_customer_profile_get_customer_email'),
    
    path('profile_customer_profile_set_customer_email/<int:instance_id>', views.profile_customer_profile_set_customer_email, name='profile_customer_profile_set_customer_email'),
    path("render_user_products", views.render_user_products, name="render_user_products"),
    path('products_product_create/', views.products_product_create, name='products_product_create'),
    path('products_product_create_popup/', views.products_product_create_popup, name='products_product_create_popup'),
    path('products_product_update/<int:instance_id>/', views.products_product_update, name='products_product_update'),
    path('products_product_update_popup/<int:instance_id>/', views.products_product_update_popup, name='products_product_update_popup'),
    path('products_product_delete/<int:instance_id>/', views.products_product_delete, name='products_product_delete'),
    
    path('products_product_get_price/<int:instance_id>', views.products_product_get_price, name='products_product_get_price'),
    
    path('products_product_set_price/<int:instance_id>', views.products_product_set_price, name='products_product_set_price'),
    
    path('products_product_set_product_description/<int:instance_id>', views.products_product_set_product_description, name='products_product_set_product_description'),
    
    path('products_product_set_product_name/<int:instance_id>', views.products_product_set_product_name, name='products_product_set_product_name'),
    
    path('products_product_get_product_description/<int:instance_id>', views.products_product_get_product_description, name='products_product_get_product_description'),
    
    path('products_product_get_product_name/<int:instance_id>', views.products_product_get_product_name, name='products_product_get_product_name'),
    ]