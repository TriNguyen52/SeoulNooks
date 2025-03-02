from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.validators import RegexValidator

class Noncoliver(models.Model):
    class Meta:
        verbose_name = _("Non-Coliver")
        verbose_name_plural = _("Non-Colivers")

    first_name = models.CharField(max_length=50, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=50, verbose_name=_("Last Name"))
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name=_("Phone Number"),
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', message=_("Enter a valid phone number."))]
    )

    email = models.EmailField(
        unique=True,  # Prevent duplicate submissions
        verbose_name=_("Email")
    )

    address = models.TextField(blank=True, verbose_name=_("Address"))

    why_join = models.TextField(verbose_name=_("Why do you want to join?"))

    special_requests = models.TextField(blank=True, verbose_name=_("Special Requests"))

    resume = models.FileField(upload_to='resumes/', blank=True, verbose_name=_("Optional upload"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Submitted On"))

    check_in_date = models.DateField(verbose_name=_("Check-in Date"), null=True, blank=True)
    move_out_date = models.DateField(verbose_name=_("Move-out Date"), null=True, blank=True)

    room_type = models.CharField(max_length=50, verbose_name=_("Room Type"), default='standard')  # Provide a default value
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Total Price"), default=0.0)  # Provide a default value
    guests = models.IntegerField(verbose_name=_("Number of Guests"), default=1)  # Provide a default value

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def get_admin_url(self):
        return reverse("admin:app_noncoliver_change", args=[self.pk])