from django.contrib import admin
from .models import Coliver

@admin.register(Coliver)
class ColiverAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'arrival_date', 'departure_date']
    search_fields = ['first_name', 'last_name', 'email']
    list_filter = ['arrival_date', 'departure_date']
