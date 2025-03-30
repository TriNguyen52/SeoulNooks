from django.db import models
from django.utils import timezone
from chapters.models import Chapter

class Coliver(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    arrival_date = models.DateField()
    departure_date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='colivers', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['-arrival_date']

