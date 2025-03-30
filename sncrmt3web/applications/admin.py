from django.contrib import admin
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'chapter', 'date_join', 'date_leave', 
                   'guests', 'member_type', 'application_status', 'is_hidden', 'created_at')
    list_filter = ('application_status', 'member_type', 'chapter', 'is_hidden', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'chapter__name')
    readonly_fields = ('created_at', 'modified_at')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        # By default, only show non-hidden applications
        return super().get_queryset(request).filter(is_hidden=False)
    
    def save_model(self, request, obj, form, change):
        print("\n=== Admin save_model called ===")
        print(f"Application: {obj.first_name} {obj.last_name}")
        print(f"Change: {change}")
        print(f"Changed data: {form.changed_data}")
        print(f"Current status: {obj.application_status}")
        
        if change and 'application_status' in form.changed_data:
            print(f"Status changed to: {obj.application_status}")
            if obj.application_status == 'Accepted':
                print("Application is being accepted")
                # Save the application to trigger the signal
                super().save_model(request, obj, form, change)
                print("Save completed")
                # Then update is_hidden using update() to avoid triggering the signal again
                Application.objects.filter(id=obj.id).update(is_hidden=True)
                print("Marked as hidden")
                return
        
        # For all other cases, just save normally
        super().save_model(request, obj, form, change)
        print("Regular save completed")