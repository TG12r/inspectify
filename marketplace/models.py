from django.db import models
from django.contrib.auth import get_user_model

class MarketplaceItem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    seller = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='marketplace_items')
    contact_info = models.CharField(max_length=200, help_text='Email, teléfono o medio de contacto')
    image = models.ImageField(upload_to='marketplace/', blank=True, null=True)
    vendido = models.BooleanField(default=False, verbose_name='Vendido')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
