from django.db import models

class Userr(models.Model):
    email = models.EmailField(unique=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=100000.00)

class Thread(models.Model):
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=500, null=True)
    user = models.ForeignKey(Userr, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    content = models.TextField(max_length=500, null=True)
    user = models.ForeignKey(Userr, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)