from django.db import models
from django.contrib.auth.models import AbstractUser
from django.shortcuts import get_object_or_404



class Product(models.Model):
    product_id = models.CharField(max_length=255, default='', null=True, blank=True)
    product_name = models.CharField(max_length=255, default='', null=True, blank=True)
    product_description = models.CharField(max_length=255, default='', null=True, blank=True)
    price = models.IntegerField(default=0, null=True, blank=True)
    cart_id = models.CharField(max_length=255, default='', null=True, blank=True)
    
    class product_category(models.TextChoices):
        ELECTRONICS = 'ELECTRONICS', 'ELECTRONICS'
        COSMETICS = 'COSMETICS', 'COSMETICS'
        FOOD = 'FOOD', 'FOOD'
        BOOKS = 'BOOKS', 'BOOKS'
        
    product_category = models.CharField(
        max_length=512,
        choices=product_category.choices,
        default=product_category.choices[0][0]
    )
    
    Cart = models.ForeignKey("Cart", on_delete=models.CASCADE, null=True, blank=True)
    


    
    def __str__(self):
        return self.product_id
    
    
    
    
    
    
    
class Customer(models.Model):
    customer_id = models.CharField(max_length=255, default='', null=True, blank=True)
    customer_name = models.CharField(max_length=255, default='', null=True, blank=True)
    customer_email = models.CharField(max_length=255, default='', null=True, blank=True)
    customer_date_of_birth = models.DateField()
    has_membership = models.BooleanField(default=False, blank=True)
    
    Cart = models.OneToOneField("Cart", on_delete=models.CASCADE)
    

    def baby_boomer_status(self):
        "Returns the person's baby-boomer status."
        import datetime

        if self.customer_date_of_birth < datetime.date(1945, 8, 1):
            return "Pre-boomer"
        elif self.customer_date_of_birth < datetime.date(1965, 1, 1):
            return "Baby boomer"
        else:
            return "Post-boomer"
    
    def __str__(self):
        return self.customer_id
    
    
    
    
    
    
    
class Cart(models.Model):
    cart_id = models.CharField(max_length=255, default='', null=True, blank=True)
    customer_id = models.CharField(max_length=255, default='', null=True, blank=True)
    num_of_items = models.IntegerField(default=0, null=True, blank=True)
    


    


    
    def __str__(self):
        return self.cart_id
    
    
