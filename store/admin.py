
# Register your models here.
from django.contrib import admin
from .models import Product
# import admin_thumbnails

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    # inlines = [ProductGalleryInline]

admin.site.register(Product,ProductAdmin)