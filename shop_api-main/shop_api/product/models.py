from django.conf import settings
from django.db import models
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return str(self.name)

class Product(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products', 
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
        null=True,
        blank=True,
    )
    def __str__(self):
        return self.title

STARS = [(i, '*' * i) for i in range(1, 6)] 
    
class Review(models.Model):
    text= models.TextField(null=True, blank=True)
    stars = models.IntegerField(choices=STARS, default=5)
    product = models.ForeignKey(
            Product, 
            on_delete=models.CASCADE, 
            related_name='reviews'
        )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Отзыв для {self.product.title} ({self.id})"

