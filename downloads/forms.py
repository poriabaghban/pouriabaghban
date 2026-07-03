from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import DownloadComment, DownloadItem, DownloadPageSetting, DownloadCategory, AllowedFileType
from .validators import validate_clean_text


class CleanTextModelForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        for field_name, value in cleaned_data.items():
            field = self.fields.get(field_name)
            if isinstance(field, (forms.CharField, forms.SlugField)) and value:
                validate_clean_text(value)
        return cleaned_data


class DownloadCategoryAdminForm(CleanTextModelForm):
    class Meta:
        model = DownloadCategory
        fields = "__all__"


class AllowedFileTypeAdminForm(CleanTextModelForm):
    class Meta:
        model = AllowedFileType
        fields = "__all__"


class DownloadItemAdminForm(CleanTextModelForm):
    class Meta:
        model = DownloadItem
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        instance = self.instance
        for name, value in cleaned_data.items():
            if name != "file":
                setattr(instance, name, value)
        if cleaned_data.get("file"):
            instance.file = cleaned_data["file"]
        instance.clean()
        return cleaned_data


class DownloadPageSettingAdminForm(CleanTextModelForm):
    class Meta:
        model = DownloadPageSetting
        fields = "__all__"


class DownloadCommentForm(forms.ModelForm):
    class Meta:
        model = DownloadComment
        fields = ("name", "comment")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Name"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Comment"}),
        }

    def clean_name(self):
        value = (self.cleaned_data["name"] or "").strip()
        validate_clean_text(value)
        return value

    def clean_comment(self):
        value = (self.cleaned_data["comment"] or "").strip()
        validate_clean_text(value)
        return value


class FrontendLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "current-password"}))
