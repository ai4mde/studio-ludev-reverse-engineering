from django.urls import path
from . import views

urlpatterns = [
    path("", views.homerender, name="admin-homerender"),
    path("render_admin_customer_cart_page", views.render_admin_customer_cart_page, name="render_admin_customer_cart_page"),
    path('customer_cart_page_customer_cart_view_create/', views.customer_cart_page_customer_cart_view_create, name='customer_cart_page_customer_cart_view_create'),
    path('customer_cart_page_customer_cart_view_create_popup/', views.customer_cart_page_customer_cart_view_create_popup, name='customer_cart_page_customer_cart_view_create_popup'),
    path('customer_cart_page_customer_cart_view_update/<int:instance_id>/', views.customer_cart_page_customer_cart_view_update, name='customer_cart_page_customer_cart_view_update'),
    path('customer_cart_page_customer_cart_view_update_popup/<int:instance_id>/', views.customer_cart_page_customer_cart_view_update_popup, name='customer_cart_page_customer_cart_view_update_popup'),
    path('customer_cart_page_customer_cart_view_delete/<int:instance_id>/', views.customer_cart_page_customer_cart_view_delete, name='customer_cart_page_customer_cart_view_delete'),
    
    path('customer_cart_page_customer_cart_view_get_num_of_items/<int:instance_id>', views.customer_cart_page_customer_cart_view_get_num_of_items, name='customer_cart_page_customer_cart_view_get_num_of_items'),
    path("render_admin_customer_page", views.render_admin_customer_page, name="render_admin_customer_page"),
    path('customer_page_customer_view_create/', views.customer_page_customer_view_create, name='customer_page_customer_view_create'),
    path('customer_page_customer_view_create_popup/', views.customer_page_customer_view_create_popup, name='customer_page_customer_view_create_popup'),
    path('customer_page_customer_view_update/<int:instance_id>/', views.customer_page_customer_view_update, name='customer_page_customer_view_update'),
    path('customer_page_customer_view_update_popup/<int:instance_id>/', views.customer_page_customer_view_update_popup, name='customer_page_customer_view_update_popup'),
    path('customer_page_customer_view_delete/<int:instance_id>/', views.customer_page_customer_view_delete, name='customer_page_customer_view_delete'),
    
    path('customer_page_customer_view_set_name/<int:instance_id>', views.customer_page_customer_view_set_name, name='customer_page_customer_view_set_name'),
    
    path('customer_page_customer_view_get_name/<int:instance_id>', views.customer_page_customer_view_get_name, name='customer_page_customer_view_get_name'),
    
    path('customer_page_customer_view_set_has_membership/<int:instance_id>', views.customer_page_customer_view_set_has_membership, name='customer_page_customer_view_set_has_membership'),
    
    path('customer_page_customer_view_get_has_membership/<int:instance_id>', views.customer_page_customer_view_get_has_membership, name='customer_page_customer_view_get_has_membership'),
    
    path('customer_page_customer_view_get_customer_email/<int:instance_id>', views.customer_page_customer_view_get_customer_email, name='customer_page_customer_view_get_customer_email'),
    
    path('customer_page_customer_view_set_customer_email/<int:instance_id>', views.customer_page_customer_view_set_customer_email, name='customer_page_customer_view_set_customer_email'),
    path("render_admin_cart_product_page", views.render_admin_cart_product_page, name="render_admin_cart_product_page"),
    path('cart_product_page_cart_product_view_create/', views.cart_product_page_cart_product_view_create, name='cart_product_page_cart_product_view_create'),
    path('cart_product_page_cart_product_view_create_popup/', views.cart_product_page_cart_product_view_create_popup, name='cart_product_page_cart_product_view_create_popup'),
    path('cart_product_page_cart_product_view_update/<int:instance_id>/', views.cart_product_page_cart_product_view_update, name='cart_product_page_cart_product_view_update'),
    path('cart_product_page_cart_product_view_update_popup/<int:instance_id>/', views.cart_product_page_cart_product_view_update_popup, name='cart_product_page_cart_product_view_update_popup'),
    path('cart_product_page_cart_product_view_delete/<int:instance_id>/', views.cart_product_page_cart_product_view_delete, name='cart_product_page_cart_product_view_delete'),
    
    path('cart_product_page_cart_product_view_get_price/<int:instance_id>', views.cart_product_page_cart_product_view_get_price, name='cart_product_page_cart_product_view_get_price'),
    
    path('cart_product_page_cart_product_view_set_price/<int:instance_id>', views.cart_product_page_cart_product_view_set_price, name='cart_product_page_cart_product_view_set_price'),
    
    path('cart_product_page_cart_product_view_set_product_name/<int:instance_id>', views.cart_product_page_cart_product_view_set_product_name, name='cart_product_page_cart_product_view_set_product_name'),
    
    path('cart_product_page_cart_product_view_set_product_description/<int:instance_id>', views.cart_product_page_cart_product_view_set_product_description, name='cart_product_page_cart_product_view_set_product_description'),
    path("render_admin_all_info_page", views.render_admin_all_info_page, name="render_admin_all_info_page"),
    path('all_info_page_customer_cart_view_create/', views.all_info_page_customer_cart_view_create, name='all_info_page_customer_cart_view_create'),
    path('all_info_page_customer_cart_view_create_popup/', views.all_info_page_customer_cart_view_create_popup, name='all_info_page_customer_cart_view_create_popup'),
    path('all_info_page_customer_cart_view_update/<int:instance_id>/', views.all_info_page_customer_cart_view_update, name='all_info_page_customer_cart_view_update'),
    path('all_info_page_customer_cart_view_update_popup/<int:instance_id>/', views.all_info_page_customer_cart_view_update_popup, name='all_info_page_customer_cart_view_update_popup'),
    path('all_info_page_customer_cart_view_delete/<int:instance_id>/', views.all_info_page_customer_cart_view_delete, name='all_info_page_customer_cart_view_delete'),
    
    path('all_info_page_customer_cart_view_get_num_of_items/<int:instance_id>', views.all_info_page_customer_cart_view_get_num_of_items, name='all_info_page_customer_cart_view_get_num_of_items'),
    path('all_info_page_customer_view_create/', views.all_info_page_customer_view_create, name='all_info_page_customer_view_create'),
    path('all_info_page_customer_view_create_popup/', views.all_info_page_customer_view_create_popup, name='all_info_page_customer_view_create_popup'),
    path('all_info_page_customer_view_update/<int:instance_id>/', views.all_info_page_customer_view_update, name='all_info_page_customer_view_update'),
    path('all_info_page_customer_view_update_popup/<int:instance_id>/', views.all_info_page_customer_view_update_popup, name='all_info_page_customer_view_update_popup'),
    path('all_info_page_customer_view_delete/<int:instance_id>/', views.all_info_page_customer_view_delete, name='all_info_page_customer_view_delete'),
    
    path('all_info_page_customer_view_set_name/<int:instance_id>', views.all_info_page_customer_view_set_name, name='all_info_page_customer_view_set_name'),
    
    path('all_info_page_customer_view_get_name/<int:instance_id>', views.all_info_page_customer_view_get_name, name='all_info_page_customer_view_get_name'),
    
    path('all_info_page_customer_view_set_has_membership/<int:instance_id>', views.all_info_page_customer_view_set_has_membership, name='all_info_page_customer_view_set_has_membership'),
    
    path('all_info_page_customer_view_get_has_membership/<int:instance_id>', views.all_info_page_customer_view_get_has_membership, name='all_info_page_customer_view_get_has_membership'),
    
    path('all_info_page_customer_view_get_customer_email/<int:instance_id>', views.all_info_page_customer_view_get_customer_email, name='all_info_page_customer_view_get_customer_email'),
    
    path('all_info_page_customer_view_set_customer_email/<int:instance_id>', views.all_info_page_customer_view_set_customer_email, name='all_info_page_customer_view_set_customer_email'),
    path('all_info_page_cart_product_view_create/', views.all_info_page_cart_product_view_create, name='all_info_page_cart_product_view_create'),
    path('all_info_page_cart_product_view_create_popup/', views.all_info_page_cart_product_view_create_popup, name='all_info_page_cart_product_view_create_popup'),
    path('all_info_page_cart_product_view_update/<int:instance_id>/', views.all_info_page_cart_product_view_update, name='all_info_page_cart_product_view_update'),
    path('all_info_page_cart_product_view_update_popup/<int:instance_id>/', views.all_info_page_cart_product_view_update_popup, name='all_info_page_cart_product_view_update_popup'),
    path('all_info_page_cart_product_view_delete/<int:instance_id>/', views.all_info_page_cart_product_view_delete, name='all_info_page_cart_product_view_delete'),
    
    path('all_info_page_cart_product_view_get_price/<int:instance_id>', views.all_info_page_cart_product_view_get_price, name='all_info_page_cart_product_view_get_price'),
    
    path('all_info_page_cart_product_view_set_price/<int:instance_id>', views.all_info_page_cart_product_view_set_price, name='all_info_page_cart_product_view_set_price'),
    
    path('all_info_page_cart_product_view_set_product_name/<int:instance_id>', views.all_info_page_cart_product_view_set_product_name, name='all_info_page_cart_product_view_set_product_name'),
    
    path('all_info_page_cart_product_view_set_product_description/<int:instance_id>', views.all_info_page_cart_product_view_set_product_description, name='all_info_page_cart_product_view_set_product_description'),
    ]