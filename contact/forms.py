from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["first_name", "last_name", "email", "phone", "message"]

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")

        if not first_name:
            raise forms.ValidationError("نام حتماً باید وارد شود.")

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")

        if not last_name:
            raise forms.ValidationError("نام خانوادگی حتماً باید وارد شود.")

        return last_name

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if not phone:
            raise forms.ValidationError("شماره تلفن حتماً باید وارد شود.")

        if not phone.startswith("09"):
            raise forms.ValidationError("شماره تلفن باید با 09 شروع شود.")

        if len(phone) != 11:
            raise forms.ValidationError("شماره تلفن باید دقیقاً ۱۱ رقم باشد.")

        if not phone.isdigit():
            raise forms.ValidationError("شماره تلفن فقط باید شامل عدد باشد.")

        return phone