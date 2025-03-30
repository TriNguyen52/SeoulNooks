from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Application
from colivers.models import Coliver
from chapters.models import Chapter
from userprofile.models import Userprofile

@receiver(post_save, sender=Application)
def handle_accepted_application(sender, instance, created, **kwargs):
    # Only process if the application was just accepted
    if not created and instance.application_status == 'Accepted':
        # Create a new Coliver record
        try:
            coliver = Coliver.objects.create(
                first_name=instance.first_name,
                last_name=instance.last_name,
                email=instance.email,
                chapter=instance.chapter,
                arrival_date=instance.date_join,
                departure_date=instance.date_leave
            )
        except Exception as e:
            return
        
        # Update the chapter status
        chapter = instance.chapter
        
        # Get the Userprofile instance for the user
        try:
            userprofile = Userprofile.objects.get(user=instance.created_by)
            chapter.booked_by = userprofile
            chapter.save()
        except Userprofile.DoesNotExist:
            # Create a Userprofile if it doesn't exist
            try:
                userprofile = Userprofile.objects.create(user=instance.created_by)
                chapter.booked_by = userprofile
                chapter.save()
            except Exception as e:
                return
        
        # Mark the application as hidden (instead of deleting it)
        if not instance.is_hidden:
            # Use update to avoid triggering the signal again
            Application.objects.filter(id=instance.id).update(is_hidden=True) 