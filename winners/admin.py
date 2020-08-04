from django.contrib import admin
from .models import Winner

# Register your models here.
class WinnerAdmin(admin.ModelAdmin):
    list_display = ('user','bid','winning_value')
    fields = ('user','bid','winning_value')
    

admin.site.register(Winner, WinnerAdmin)