from django.db import models
from django.utils.timezone import now

class EmailLog(models.Model):
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Email to {self.recipient} at {self.sent_at}"
