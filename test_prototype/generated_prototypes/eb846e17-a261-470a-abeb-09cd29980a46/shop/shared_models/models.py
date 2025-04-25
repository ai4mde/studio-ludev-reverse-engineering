from django.db import models
import datetime

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

    def baby_boomer_status(self):
        "Returns the person's baby-boomer status."
        if self.customer_date_of_birth < datetime.date(1945, 8, 1):
            return "Pre-boomer"
        elif self.customer_date_of_birth < datetime.date(1965, 1, 1):
            return "Baby boomer"
        else:
            return "Post-boomer"

    def calculate_subscription_type(self):
        """
        Determines the subscription type based on Customer's attributes.
        This method represents a functional dependency on the Customer model's data.
        """
        if self.has_membership:
            if self.baby_boomer_status() == "Baby boomer":
                return "Premium Membership"
            else:
                return "Standard Membership"
        else:
            return "Basic Membership"


    def __str__(self):
        return self.customer_id

class DigitalWallet(models.Model):
    wallet_id = models.CharField(max_length=255, default='', null=True, blank=True)
    balance = models.IntegerField(default=0, null=True, blank=True)

    #Composition: Each customer has exactly one wallet, when customer is deleted,the related wallet should be gone also
    customer = models.OneToOneField('Customer', on_delete=models.CASCADE)
    def __str__(self):
        return self.wallet_id

class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    cart_id = models.CharField(max_length=255, default='', null=True, blank=True)
    num_of_items = models.IntegerField(default=0, null=True, blank=True)

    customer = models.OneToOneField("Customer", on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.cart_id

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.CharField(max_length=255, default='', null=True, blank=True)
    product_name = models.CharField(max_length=255, default='', null=True, blank=True)
    product_description = models.CharField(max_length=255, default='', null=True, blank=True)
    price = models.IntegerField(default=0, null=True, blank=True)

    # Association: Many products belong to one cart
    Cart = models.ForeignKey('Cart', null=True, on_delete=models.CASCADE, related_name='products')

    # Dependency: Product depends on an enum for category (shown in diagram)
    category = models.CharField(max_length=20, choices=ProductCategory.choices, default=ProductCategory.ELECTRONICS)

    def __str__(self):
        return self.product_id

# Generalization: DigitalProduct is a subtype of Product
class DigitalProduct(Product):
    license_key = models.CharField(max_length=255, default='', null=True, blank=True)

    def __str__(self):
        return self.license_key

# Generalization: DigitalProduct is a subtype of Product
class LimitedProduct(Product):
    license_key = models.CharField(max_length=255, default='', null=True, blank=True)

    def __str__(self):
        return self.license_key

class SpecialLimitedProduct(LimitedProduct):
    special_content = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.special_content} - special limited product"

class Membership(models.Model):
    id = models.AutoField(primary_key=True)
    subscription_id = models.CharField(max_length=255, default='', null=True, blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    subscription_type = models.CharField(max_length=255, default='', null=True, blank=True)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.subscription_id
