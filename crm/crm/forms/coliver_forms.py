from django import forms
from crm.models.coliver import Coliver

class ColiverForm(forms.ModelForm):
    class Meta:
        model = Coliver
        fields = ["name", "email"]  # Add relevant fields
