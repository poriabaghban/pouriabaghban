from django import forms
from .models import ContactMessage
from pouriabaghban3.input_validation import validate_no_forbidden_user_input

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام شما'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ایمیل شما'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شماره تماس (اختیاری)'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'موضوع'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'پیام خود را بنویسید...', 'rows': 5}),
        }

    def clean(self):
        cleaned_data = super().clean()
        for field in self.fields:
            value = cleaned_data.get(field)
            if isinstance(value, str):
                validate_no_forbidden_user_input(value)
        return cleaned_data
