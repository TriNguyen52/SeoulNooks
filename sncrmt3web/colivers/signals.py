from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Coliver
from chapters.models import Chapter

@receiver(post_delete, sender=Coliver)
def handle_coliver_deletion(sender, instance, **kwargs):
    print(f"\n=== Processing Coliver deletion ===")
    print(f"Coliver: {instance.first_name} {instance.last_name}")
    
    # When a Coliver is deleted, make their chapter available again
    if instance.chapter:
        chapter = instance.chapter
        print(f"Chapter before update: {chapter.name} (booked_by: {chapter.booked_by})")
        chapter.booked_by = None
        chapter.save()
        print(f"Chapter after update: {chapter.name} (booked_by: {chapter.booked_by})") 