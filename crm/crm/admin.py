from django.contrib import admin
from crm.models.noncoliver import Noncoliver
from crm.models.coliver import Coliver

@admin.register(Noncoliver)
class NoncoliverAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "created_at")
    actions = ["approve_and_move_to_coliver"]

    def approve_and_move_to_coliver(self, request, queryset):
        for noncoliver in queryset:
            # Create a new Coliver instance
            Coliver.objects.create(
                first_name=noncoliver.first_name,
                last_name=noncoliver.last_name,
                phone=noncoliver.phone,
                email=noncoliver.email,
                address=noncoliver.address,
                why_join=noncoliver.why_join,
                resume=noncoliver.resume,
            )

            # Delete from Noncoliver
            noncoliver.delete()

        self.message_user(request, "Selected applicants have been approved and moved to Coliver.")

    approve_and_move_to_coliver.short_description = "Approve and move to Coliver"

@admin.register(Coliver)
class ColiverAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "joined_at")
