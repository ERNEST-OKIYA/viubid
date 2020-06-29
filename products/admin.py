from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ('code','name', 'description','price',)
    # fields = ('name','description','image','width','height')
    display_links = ('name')
    list_filter = ('name',)
    # readonly_fields = ('width','height')
    fieldsets = (
        (None, {'fields': ('code','name', 'description','offered')}),
        ('Image', {'fields': ('image', 'width', 'height','price',)}),

    )
admin.site.register(Product, ProductAdmin)