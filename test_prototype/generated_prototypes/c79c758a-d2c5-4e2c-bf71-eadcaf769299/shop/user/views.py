from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from shared_models.models import *


def shopping_cart_customer_cart_get_num_of_items(request, instance_id):
    instance = get_object_or_404(Cart, pk=instance_id)
    instance.()
    context = {}
    context['Cart_list'] = Cart.objects.all()
    return render(request, 'user_shopping_cart.html', context)




def profile_customer_profile_create(request):
    if request.method == 'POST':
        new_object = Customer()
        if request.POST.get('instance_customer_id') == '':
            new_object.customer_id = None
        else:
            new_object.customer_id = request.POST.get('instance_customer_id')

        if request.POST.get('instance_customer_name') == '':
            new_object.customer_name = None
        else:
            new_object.customer_name = request.POST.get('instance_customer_name')

        if request.POST.get('instance_customer_email') == '':
            new_object.customer_email = None
        else:
            new_object.customer_email = request.POST.get('instance_customer_email')

        if request.POST.get('instance_customer_date_of_birth') == '':
            new_object.customer_date_of_birth = None
        else:
            new_object.customer_date_of_birth = request.POST.get('instance_customer_date_of_birth')

        new_object.has_membership = (request.POST.get('instance_has_membership') == 'on')
        new_object.save()
    return redirect('render_user_profile')

def profile_customer_profile_create_popup(request):
    context = {}
    context['Customer_list'] = Customer.objects.all()
    context['customer_profile_create_popup'] = True
    return render(request, 'user_profile.html', context)


def profile_customer_profile_delete(request, instance_id):
    if request.method == 'POST':
        instance = get_object_or_404(Customer, pk=instance_id)
        instance.delete()
        return redirect('render_user_profile')

def profile_customer_profile_update(request, instance_id):
    if request.method == 'POST':
        instance = get_object_or_404(Customer, pk=instance_id)
        instance.customer_id = request.POST.get('instance_customer_id')
        instance.customer_name = request.POST.get('instance_customer_name')
        instance.customer_email = request.POST.get('instance_customer_email')
        instance.customer_date_of_birth = request.POST.get('instance_customer_date_of_birth')
        instance.has_membership = (request.POST.get('instance_has_membership') == 'on')
        instance.save()
        return redirect('render_user_profile')

def profile_customer_profile_update_popup(request, instance_id):
    context = {}
    context['Customer_list'] = Customer.objects.all()
    context['update_instance'] = get_object_or_404(Customer, pk=instance_id)
    return render(request, 'user_profile.html', context)


def profile_customer_profile_get_name(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Customer_list'] = Customer.objects.all()
    return render(request, 'user_profile.html', context)
def profile_customer_profile_set_name(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Customer_list'] = Customer.objects.all()
    return render(request, 'user_profile.html', context)
def profile_customer_profile_set_has_membership(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Customer_list'] = Customer.objects.all()
    return render(request, 'user_profile.html', context)
def profile_customer_profile_get_has_membership(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Customer_list'] = Customer.objects.all()
    return render(request, 'user_profile.html', context)
def profile_customer_profile_get_customer_email(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Customer_list'] = Customer.objects.all()
    return render(request, 'user_profile.html', context)
def profile_customer_profile_set_customer_email(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Customer_list'] = Customer.objects.all()
    return render(request, 'user_profile.html', context)




def products_product_create(request):
    if request.method == 'POST':
        new_object = Product()
        if request.POST.get('instance_product_id') == '':
            new_object.product_id = None
        else:
            new_object.product_id = request.POST.get('instance_product_id')

        if request.POST.get('instance_product_name') == '':
            new_object.product_name = None
        else:
            new_object.product_name = request.POST.get('instance_product_name')

        if request.POST.get('instance_product_description') == '':
            new_object.product_description = None
        else:
            new_object.product_description = request.POST.get('instance_product_description')

        if request.POST.get('instance_price') == '':
            new_object.price = None
        else: 
            new_object.price = request.POST.get('instance_price')
        if request.POST.get('instance_cart_id') == '':
            new_object.cart_id = None
        else:
            new_object.cart_id = request.POST.get('instance_cart_id')

        if request.POST.get('instance_product_category') == '':
            new_object.product_category = None
        else:
            new_object.product_category = request.POST.get('instance_product_category')

        new_object.save()
    return redirect('render_user_products')

def products_product_create_popup(request):
    context = {}
    context['Product_list'] = Product.objects.all()
    context['product_create_popup'] = True
    return render(request, 'user_products.html', context)


def products_product_delete(request, instance_id):
    if request.method == 'POST':
        instance = get_object_or_404(Product, pk=instance_id)
        instance.delete()
        return redirect('render_user_products')

def products_product_update(request, instance_id):
    if request.method == 'POST':
        instance = get_object_or_404(Product, pk=instance_id)
        instance.product_id = request.POST.get('instance_product_id')
        instance.product_name = request.POST.get('instance_product_name')
        instance.product_description = request.POST.get('instance_product_description')
        instance.price = request.POST.get('instance_price')
        instance.cart_id = request.POST.get('instance_cart_id')
        instance.product_category = request.POST.get('instance_product_category')
        instance.save()
        return redirect('render_user_products')

def products_product_update_popup(request, instance_id):
    context = {}
    context['Product_list'] = Product.objects.all()
    context['update_instance'] = get_object_or_404(Product, pk=instance_id)
    return render(request, 'user_products.html', context)


def products_product_get_price(request, instance_id):
    instance = get_object_or_404(Product, pk=instance_id)
    instance.()
    context = {}
    context['Product_list'] = Product.objects.all()
    return render(request, 'user_products.html', context)
def products_product_set_price(request, instance_id):
    instance = get_object_or_404(Product, pk=instance_id)
    instance.()
    context = {}
    context['Product_list'] = Product.objects.all()
    return render(request, 'user_products.html', context)
def products_product_set_product_description(request, instance_id):
    instance = get_object_or_404(Product, pk=instance_id)
    instance.()
    context = {}
    context['Product_list'] = Product.objects.all()
    return render(request, 'user_products.html', context)
def products_product_set_product_name(request, instance_id):
    instance = get_object_or_404(Product, pk=instance_id)
    instance.()
    context = {}
    context['Product_list'] = Product.objects.all()
    return render(request, 'user_products.html', context)
def products_product_get_product_description(request, instance_id):
    instance = get_object_or_404(Product, pk=instance_id)
    instance.()
    context = {}
    context['Product_list'] = Product.objects.all()
    return render(request, 'user_products.html', context)
def products_product_get_product_name(request, instance_id):
    instance = get_object_or_404(Product, pk=instance_id)
    instance.()
    context = {}
    context['Product_list'] = Product.objects.all()
    return render(request, 'user_products.html', context)




def render_user_shopping_cart(request):
    context = {}
    context['Cart_list'] = Cart.objects.all()
    return render(request, 'user_shopping_cart.html', context)

def render_user_profile(request):
    context = {}
    context['Customer_list'] = Customer.objects.all()
    return render(request, 'user_profile.html', context)

def render_user_products(request):
    context = {}
    context['Product_list'] = Product.objects.all()
    return render(request, 'user_products.html', context)


def homerender(request):
    context = {}
    context['user'] = request.user
    return render(request, 'user_home.html', context)