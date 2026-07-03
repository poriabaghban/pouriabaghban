from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import KskhComment, KskhPost
from .validators import validate_clean_text


class KskhLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "kskh-input", "autocomplete": "username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "kskh-input", "autocomplete": "current-password"}))


class KskhPostForm(forms.ModelForm):
    class Meta:
        model = KskhPost
        fields = ("title", "description", "file")
        widgets = {
            "title": forms.TextInput(attrs={"class": "kskh-input", "placeholder": "عنوان فایل"}),
            "description": forms.Textarea(attrs={"class": "kskh-input", "rows": 4, "placeholder": "توضیح کوتاه درباره app یا کانفیگ"}),
            "file": forms.ClearableFileInput(attrs={"class": "kskh-input"}),
        }

    def clean_title(self):
        value = (self.cleaned_data.get("title") or "").strip()
        validate_clean_text(value)
        return value

    def clean_description(self):
        value = (self.cleaned_data.get("description") or "").strip()
        validate_clean_text(value)
        return value


class KskhCommentForm(forms.ModelForm):
    parent_id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = KskhComment
        fields = ("body",)
        widgets = {
            "body": forms.Textarea(attrs={"class": "kskh-input", "rows": 3, "placeholder": "کامنت یا ریپلای شما"}),
        }

    def clean_body(self):
        value = (self.cleaned_data.get("body") or "").strip()
        validate_clean_text(value)
        return value
