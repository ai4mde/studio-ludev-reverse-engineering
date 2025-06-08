from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from shared_models.models import *




def customer_cart_page_customer_cart_view_create(request):
    if request.method == 'POST':
        new_object = Cart()
        if request.POST.get('instance_cart_id') == '':
            new_object.cart_id = None
        else:
            new_object.cart_id = request.POST.get('instance_cart_id')

        if request.POST.get('instance_customer_id') == '':
            new_object.customer_id = None
        else:
            new_object.customer_id = request.POST.get('instance_customer_id')

        if request.POST.get('instance_num_of_items') == '':
            new_object.num_of_items = None
        else: 
            new_object.num_of_items = request.POST.get('instance_num_of_items')
        new_object.save()
    return redirect('render_admin_customer_cart_page')

def customer_cart_page_customer_cart_view_create_popup(request):
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['customer_cart_view_create_popup'] = True
    return render(request, 'admin_customer_cart_page.html', context)


def customer_cart_page_customer_cart_view_delete(request, instance_id):
    if request.method == 'POST':
        instance = get_object_or_404(Cart, pk=instance_id)
        instance.delete()
        return redirect('render_admin_customer_cart_page')

def customer_cart_page_customer_cart_view_update(request, instance_id):
    if request.method == 'POST':
        instance = get_object_or_404(Cart, pk=instance_id)
        instance.cart_id = request.POST.get('instance_cart_id')
        instance.customer_id = request.POST.get('instance_customer_id')
        instance.num_of_items = request.POST.get('instance_num_of_items')
        instance.save()
        return redirect('render_admin_customer_cart_page')

def customer_cart_page_customer_cart_view_update_popup(request, instance_id):
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['update_instance'] = get_object_or_404(Cart, pk=instance_id)
    return render(request, 'admin_customer_cart_page.html', context)


def customer_cart_page_customer_cart_view_get_num_of_items(request, instance_id):
    instance = get_object_or_404(Cart, pk=instance_id)
    instance.()
    context = {}
    context['Cart_list'] = Cart.objects.all()
    return render(request, 'admin_customer_cart_page.html', context)




def customer_page_customer_view_create(request):
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

        new_object.save()
    return redirect('render_admin_customer_page')

def customer_page_customer_view_create_popup(request):
    context = {}
    context['Customer_list'] = Customer.objects.all()
    context['customer_view_create_popup'] = True
    return render(request, 'admin_customer_page.html', context)


def customer_page_customer_view_delete(request, instance_id):
    if request.method == 'POST':
        instance = get_object_or_404(Customer, pk=instance_id)
        instance.delete()
        return redirect('render_admin_customer_page')

def customer_page_customer_view_update(request, instance_id):
    if request.method == 'POST':
        instance = get_object_or_404(Customer, pk=instance_id)
        instance.customer_id = request.POST.get('instance_customer_id')
        instance.customer_name = request.POST.get('instance_customer_name')
        instance.customer_email = request.POST.get('instance_customer_email')
        instance.customer_date_of_birth = request.POST.get('instance_customer_date_of_birth')
        instance.save()
        return redirect('render_admin_customer_page')

def customer_page_customer_view_update_popup(request, instance_id):
    context = {}
    context['Customer_list'] = Customer.objects.all()
    context['update_instance'] = get_object_or_404(Customer, pk=instance_id)
    return render(request, 'admin_customer_page.html', context)


def customer_page_customer_view_set_name(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Customer_list'] = Customer.objects.all()
    return render(request, 'admin_customer_page.html', context)
def customer_page_customer_view_get_name(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Customer_list'] = Customer.objects.all()
    return render(request, 'admin_customer_page.html', context)
def customer_page_customer_view_set_has_membership(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Customer_list'] = Customer.objects.all()
    return render(request, 'admin_customer_page.html', context)
def customer_page_customer_view_get_has_membership(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Customer_list'] = Customer.objects.all()
    return render(request, 'admin_customer_page.html', context)
def customer_page_customer_view_get_customer_email(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Customer_list'] = Customer.objects.all()
    return render(request, 'admin_customer_page.html', context)
def customer_page_customer_view_set_customer_email(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Customer_list'] = Customer.objects.all()
    return render(request, 'admin_customer_page.html', context)




def cart_product_page_cart_product_view_create(request):
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

        new_object.save()
    return redirect('render_admin_cart_product_page')

def cart_product_page_cart_product_view_create_popup(request):
    context = {}
    context['Product_list'] = Product.objects.all()
    context['cart_product_view_create_popup'] = True
    return render(request, 'admin_cart_product_page.html', context)


def cart_product_page_cart_product_view_delete(request, instance_id):
    if request.method == 'POST':
        instance = get_object_or_404(Product, pk=instance_id)
        instance.delete()
        return redirect('render_admin_cart_product_page')

def cart_product_page_cart_product_view_update(request, instance_id):
    if request.method == 'POST':
        instance = get_object_or_404(Product, pk=instance_id)
        instance.product_id = request.POST.get('instance_product_id')
        instance.product_name = request.POST.get('instance_product_name')
        instance.product_description = request.POST.get('instance_product_description')
        instance.price = request.POST.get('instance_price')
        instance.cart_id = request.POST.get('instance_cart_id')
        instance.save()
        return redirect('render_admin_cart_product_page')

def cart_product_page_cart_product_view_update_popup(request, instance_id):
    context = {}
    context['Product_list'] = Product.objects.all()
    context['update_instance'] = get_object_or_404(Product, pk=instance_id)
    return render(request, 'admin_cart_product_page.html', context)


def cart_product_page_cart_product_view_get_price(request, instance_id):
    instance = get_object_or_404(Product, pk=instance_id)
    instance.()
    context = {}
    context['Product_list'] = Product.objects.all()
    return render(request, 'admin_cart_product_page.html', context)
def cart_product_page_cart_product_view_set_price(request, instance_id):
    instance = get_object_or_404(Product, pk=instance_id)
    instance.()
    context = {}
    context['Product_list'] = Product.objects.all()
    return render(request, 'admin_cart_product_page.html', context)
def cart_product_page_cart_product_view_set_product_name(request, instance_id):
    instance = get_object_or_404(Product, pk=instance_id)
    instance.()
    context = {}
    context['Product_list'] = Product.objects.all()
    return render(request, 'admin_cart_product_page.html', context)
def cart_product_page_cart_product_view_set_product_description(request, instance_id):
    instance = get_object_or_404(Product, pk=instance_id)
    instance.()
    context = {}
    context['Product_list'] = Product.objects.all()
    return render(request, 'admin_cart_product_page.html', context)




def all_info_page_customer_cart_view_create(request):
    if request.method == 'POST':
        new_object = Cart()
        if request.POST.get('instance_cart_id') == '':
            new_object.cart_id = None
        else:
            new_object.cart_id = request.POST.get('instance_cart_id')

        if request.POST.get('instance_customer_id') == '':
            new_object.customer_id = None
        else:
            new_object.customer_id = request.POST.get('instance_customer_id')

        if request.POST.get('instance_num_of_items') == '':
            new_object.num_of_items = None
        else: 
            new_object.num_of_items = request.POST.get('instance_num_of_items')
        new_object.save()
    return redirect('render_admin_all_info_page')

def all_info_page_customer_cart_view_create_popup(request):
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    context['customer_cart_view_create_popup'] = True
    return render(request, 'admin_all_info_page.html', context)


def all_info_page_customer_cart_view_delete(request, instance_id):
    if request.method == 'POST':
        instance = get_object_or_404(Cart, pk=instance_id)
        instance.delete()
        return redirect('render_admin_all_info_page')

def all_info_page_customer_cart_view_update(request, instance_id):
    if request.method == 'POST':
        instance = get_object_or_404(Cart, pk=instance_id)
        instance.cart_id = request.POST.get('instance_cart_id')
        instance.customer_id = request.POST.get('instance_customer_id')
        instance.num_of_items = request.POST.get('instance_num_of_items')
        instance.save()
        return redirect('render_admin_all_info_page')

def all_info_page_customer_cart_view_update_popup(request, instance_id):
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    context['update_instance'] = get_object_or_404(Cart, pk=instance_id)
    return render(request, 'admin_all_info_page.html', context)


def all_info_page_customer_cart_view_get_num_of_items(request, instance_id):
    instance = get_object_or_404(Cart, pk=instance_id)
    instance.()
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    return render(request, 'admin_all_info_page.html', context)


def all_info_page_customer_view_create(request):
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

        new_object.save()
    return redirect('render_admin_all_info_page')

def all_info_page_customer_view_create_popup(request):
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    context['customer_view_create_popup'] = True
    return render(request, 'admin_all_info_page.html', context)


def all_info_page_customer_view_delete(request, instance_id):
    if request.method == 'POST':
        instance = get_object_or_404(Customer, pk=instance_id)
        instance.delete()
        return redirect('render_admin_all_info_page')

def all_info_page_customer_view_update(request, instance_id):
    if request.method == 'POST':
        instance = get_object_or_404(Customer, pk=instance_id)
        instance.customer_id = request.POST.get('instance_customer_id')
        instance.customer_name = request.POST.get('instance_customer_name')
        instance.customer_email = request.POST.get('instance_customer_email')
        instance.customer_date_of_birth = request.POST.get('instance_customer_date_of_birth')
        instance.save()
        return redirect('render_admin_all_info_page')

def all_info_page_customer_view_update_popup(request, instance_id):
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    context['update_instance'] = get_object_or_404(Customer, pk=instance_id)
    return render(request, 'admin_all_info_page.html', context)


def all_info_page_customer_view_set_name(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    return render(request, 'admin_all_info_page.html', context)
def all_info_page_customer_view_get_name(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    return render(request, 'admin_all_info_page.html', context)
def all_info_page_customer_view_set_has_membership(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    return render(request, 'admin_all_info_page.html', context)
def all_info_page_customer_view_get_has_membership(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    return render(request, 'admin_all_info_page.html', context)
def all_info_page_customer_view_get_customer_email(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    return render(request, 'admin_all_info_page.html', context)
def all_info_page_customer_view_set_customer_email(request, instance_id):
    instance = get_object_or_404(Customer, pk=instance_id)
    instance.()
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    return render(request, 'admin_all_info_page.html', context)


def all_info_page_cart_product_view_create(request):
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

        new_object.save()
    return redirect('render_admin_all_info_page')

def all_info_page_cart_product_view_create_popup(request):
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    context['cart_product_view_create_popup'] = True
    return render(request, 'admin_all_info_page.html', context)


def all_info_page_cart_product_view_delete(request, instance_id):
    if request.method == 'POST':
        instance = get_object_or_404(Product, pk=instance_id)
        instance.delete()
        return redirect('render_admin_all_info_page')

def all_info_page_cart_product_view_update(request, instance_id):
    if request.method == 'POST':
        instance = get_object_or_404(Product, pk=instance_id)
        instance.product_id = request.POST.get('instance_product_id')
        instance.product_name = request.POST.get('instance_product_name')
        instance.product_description = request.POST.get('instance_product_description')
        instance.price = request.POST.get('instance_price')
        instance.cart_id = request.POST.get('instance_cart_id')
        instance.save()
        return redirect('render_admin_all_info_page')

def all_info_page_cart_product_view_update_popup(request, instance_id):
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    context['update_instance'] = get_object_or_404(Product, pk=instance_id)
    return render(request, 'admin_all_info_page.html', context)


def all_info_page_cart_product_view_get_price(request, instance_id):
    instance = get_object_or_404(Product, pk=instance_id)
    instance.()
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    return render(request, 'admin_all_info_page.html', context)
def all_info_page_cart_product_view_set_price(request, instance_id):
    instance = get_object_or_404(Product, pk=instance_id)
    instance.()
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    return render(request, 'admin_all_info_page.html', context)
def all_info_page_cart_product_view_set_product_name(request, instance_id):
    instance = get_object_or_404(Product, pk=instance_id)
    instance.()
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    return render(request, 'admin_all_info_page.html', context)
def all_info_page_cart_product_view_set_product_description(request, instance_id):
    instance = get_object_or_404(Product, pk=instance_id)
    instance.()
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    return render(request, 'admin_all_info_page.html', context)




def render_admin_customer_cart_page(request):
    context = {}
    context['Cart_list'] = Cart.objects.all()
    return render(request, 'admin_customer_cart_page.html', context)

def render_admin_customer_page(request):
    context = {}
    context['Customer_list'] = Customer.objects.all()
    return render(request, 'admin_customer_page.html', context)

def render_admin_cart_product_page(request):
    context = {}
    context['Product_list'] = Product.objects.all()
    return render(request, 'admin_cart_product_page.html', context)

def render_admin_all_info_page(request):
    context = {}
    context['Cart_list'] = Cart.objects.all()
    context['Customer_list'] = Customer.objects.all()
    context['Product_list'] = Product.objects.all()
    return render(request, 'admin_all_info_page.html', context)


def homerender(request):
    context = {}
    context['user'] = request.user
    return render(request, 'admin_home.html', context)