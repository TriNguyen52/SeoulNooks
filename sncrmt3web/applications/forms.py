from django import forms
from datetime import datetime, timedelta
from django.utils.safestring import mark_safe

from .models import Application

class ApplicationDatesForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['first_name', 'last_name', 'email', 'date_join', 'date_leave', 'guests', 'member_type']
        widgets = {
            'date_join': forms.DateInput(attrs={'type': 'date', 'required': True}),
            'date_leave': forms.DateInput(attrs={'type': 'date', 'required': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make personal info fields optional
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['email'].required = False

    def clean(self):
        cleaned_data = super().clean()
        date_join = cleaned_data.get('date_join')
        date_leave = cleaned_data.get('date_leave')

        if not date_join:
            raise forms.ValidationError('Arrival date is required.')
        if not date_leave:
            raise forms.ValidationError('Departure date is required.')

        if date_join and date_leave:
            min_leave_date = date_join + timedelta(days=28)
            max_leave_date = date_join + timedelta(days=62)
            if date_leave < min_leave_date:
                raise forms.ValidationError(mark_safe('<i> Bookings must be for at least 1 month 🌸 </i>'))
            if date_leave > max_leave_date:
                raise forms.ValidationError(mark_safe('<i> Initial bookings cannot exceed 2 months 🌸 </i>'))
        return cleaned_data

class ApplicationNameForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['question_1', 'question_2', 'question_3']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional by default
        self.fields['question_1'].required = False
        self.fields['question_2'].required = False
        self.fields['question_3'].required = False

    def clean(self):
        cleaned_data = super().clean()
        if self.data.get('submit'):
            if not cleaned_data.get('question_1'):
                self.add_error('question_1', 'This field is required for submission.')
            if not cleaned_data.get('question_2'):
                self.add_error('question_2', 'This field is required for submission.')
            if not cleaned_data.get('question_3'):
                self.add_error('question_3', 'This field is required for submission.')
        return cleaned_data

class ApplicationEditForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['first_name', 'last_name', 'email', 'date_join', 'date_leave', 
                 'guests', 'member_type', 'question_1', 'question_2', 'question_3', 'chapter']
        widgets = {
            'date_join': forms.DateInput(attrs={'type': 'date', 'required': True}),
            'date_leave': forms.DateInput(attrs={'type': 'date', 'required': True}),
            'question_1': forms.Textarea(attrs={'rows': 4}),
            'question_2': forms.Textarea(attrs={'rows': 4}),
            'question_3': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_join = cleaned_data.get('date_join')
        date_leave = cleaned_data.get('date_leave')

        if not date_join:
            raise forms.ValidationError('Arrival date is required')
        if not date_leave:
            raise forms.ValidationError('Departure date is required')

        if date_join and date_leave:
            min_leave_date = date_join + timedelta(days=28)
            max_leave_date = date_join + timedelta(days=62)
            if date_leave < min_leave_date:
                raise forms.ValidationError(mark_safe('<i> Bookings must be for at least 1 month 🌸 </i>'))
            if date_leave > max_leave_date:
                raise forms.ValidationError(mark_safe('<i> Initial bookings cannot exceed 2 months 🌸 </i>'))
        return cleaned_data
