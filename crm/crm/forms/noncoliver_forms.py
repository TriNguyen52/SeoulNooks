from django import forms
from crm.models.noncoliver import Noncoliver

class NoncoliverForm(forms.ModelForm):
    class Meta:
        model = Noncoliver
        fields = ["first_name", "last_name", "phone", "email", "check_in_date", "move_out_date", "guests", "room_type", "total_price", "address", "why_join", "special_requests"]
        widgets = {
            "check_in_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "move_out_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }