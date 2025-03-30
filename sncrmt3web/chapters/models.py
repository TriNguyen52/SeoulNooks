from django.db import models
from django.contrib.auth.models import User
from userprofile.models import Userprofile

class Chapter(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    cost_per_night = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Cost per night in USD",
        default=0.00
    )

    created_by = models.ForeignKey(User, related_name='chapters', on_delete=models.CASCADE)
    booked_by = models.ForeignKey(Userprofile, related_name='booked_chapters', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        if not self.created_by.is_staff:
            raise PermissionError("Only admin users can create chapters.")
        super().save(*args, **kwargs)

class ChapterBooking(models.Model):
    chapter = models.ForeignKey(Chapter, related_name='booking', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    
    class Meta:
        ordering = ['start_date']
        
    def __str__(self):
        return f"{self.chapter.name}: {self.start_date} to {self.end_date}"

class ChapterImage(models.Model):
    chapter = models.ForeignKey(
        Chapter, 
        related_name='images', 
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to='chapter_images/',
        help_text="Upload an image for this chapter"
    )
    order = models.IntegerField(
        default=0,
        help_text="Order in which the image will be displayed"
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.chapter.name}"
