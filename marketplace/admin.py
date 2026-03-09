from django.contrib import admin
from .models import MarketplaceItem

@admin.register(MarketplaceItem)
class MarketplaceItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'price', 'created_at')
    search_fields = ('title', 'description', 'seller__username')
