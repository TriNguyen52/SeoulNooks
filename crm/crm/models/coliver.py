from django.db import models
from django.utils.translation import gettext_lazy as _

class Coliver(models.Model):
    class Meta:
        verbose_name = _("Coliver")
        verbose_name_plural = _("Colivers")

    first_name = models.CharField(max_length=50, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=50, verbose_name=_("Last Name"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Phone Number"))
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    address = models.TextField(blank=True, verbose_name=_("Address"))
    why_join = models.TextField(verbose_name=_("Why did you join?"))
    resume = models.FileField(upload_to="resumes/", blank=True, verbose_name=_("Resume"))
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Joined On"))

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
