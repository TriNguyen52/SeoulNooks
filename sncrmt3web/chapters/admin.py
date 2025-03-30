from django.contrib import admin

# Register your models here.
from .models import Chapter, ChapterBooking, ChapterImage

class ChapterBookingsInline(admin.TabularInline):
    model = ChapterBooking
    extra = 1

class ChapterImageInline(admin.TabularInline):
    model = ChapterImage
    extra = 1  # Number of empty forms to display

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost_per_night']
    search_fields = ['name']
    inlines = [ChapterBookingsInline, ChapterImageInline]
    ordering = ['name']  # Sort by name by default

    fields = ('name', 'description', 'cost_per_night')  # `created_by` is excluded

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set created_by during creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

