from django.db import models
from django.contrib.auth.models import AbstractUser
from django.shortcuts import get_object_or_404

# Enum class for product categories
class ProductCategory(models.TextChoices):
    ELECTRONICS = 'ELECTRONICS', 'Electronics'
    COSMETICS = 'COSMETICS', 'Cosmetics'
    FOOD = 'FOOD', 'Food'
    BOOKS = 'BOOKS', 'Books'


class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    customer_id = models.CharField(max_length=255, default='', null=True, blank=True)
    customer_name = models.CharField(max_length=255, default='', null=True, blank=True)
    customer_email = models.CharField(max_length=255, default='', null=True, blank=True)
    customer_date_of_birth = models.DateTimeField(null=True, blank=True)
    has_membership = models.BooleanField(default=False, blank=True)

    # Composition: Each customer has exactly one wallet
    digital_wallet = models.OneToOneField('DigitalWallet', on_delete=models.CASCADE)

    def __str__(self):
        return self.customer_id


class DigitalWallet(models.Model):
    wallet_id = models.CharField(max_length=255, default='', null=True, blank=True)
    balance = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.wallet_id


class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    cart_id = models.CharField(max_length=255, default='', null=True, blank=True)
    num_of_items = models.IntegerField(default=0, null=True, blank=True)

    # Association: One cart belongs to one customer
    customer = models.OneToOneField('Customer', on_delete=models.CASCADE)

    def __str__(self):
        return self.cart_id


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.CharField(max_length=255, default='', null=True, blank=True)
    product_name = models.CharField(max_length=255, default='', null=True, blank=True)
    product_description = models.CharField(max_length=255, default='', null=True, blank=True)
    price = models.IntegerField(default=0, null=True, blank=True)

    # Association: Many products belong to one cart
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='products')

    # Dependency: Product depends on an enum for category (shown in diagram)
    category = models.CharField(max_length=20, choices=ProductCategory.choices, default=ProductCategory.ELECTRONICS)

    def __str__(self):
        return self.product_id


# Generalization: DigitalProduct is a subtype of Product
class DigitalProduct(Product):
    license_key = models.CharField(max_length=255, default='', null=True, blank=True)

    def __str__(self):
        return self.license_key
