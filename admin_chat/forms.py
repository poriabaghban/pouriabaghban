import os

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from .models import ChatRoom
from downloads.validators import validate_clean_text


class ChatRoomAdminForm(forms.ModelForm):
    class Meta:
        model = ChatRoom
        fields = "__all__"

    def clean_participants(self):
        participants = self.cleaned_data.get("participants")
        if participants:
            non_staff = participants.filter(is_staff=False).first()
            if non_staff:
                raise ValidationError("فقط کاربران ادمین می‌توانند عضو اتاق چت باشند.")
        return participants

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        validate_clean_text(name)
        return name


class ChunkUploadForm(forms.Form):
    room_id = forms.IntegerField(min_value=1)
    message_id = forms.IntegerField(min_value=1)
    upload_id = forms.CharField(max_length=80)
    file_name = forms.CharField(max_length=255)
    file_type = forms.CharField(max_length=150, required=False)
    file_size = forms.IntegerField(min_value=1)
    chunk_index = forms.IntegerField(min_value=0)
    total_chunks = forms.IntegerField(min_value=1)
    chunk = forms.FileField()

    def clean_file_name(self):
        file_name = os.path.basename(self.cleaned_data["file_name"])
        validate_clean_text(file_name)
        ext = os.path.splitext(file_name)[1].lower()
        file_type = (self.data.get("file_type") or "").lower()
        if file_type.startswith("image/"):
            return file_name
        allowed = getattr(settings, "CHAT_ALLOWED_ATTACHMENT_EXTENSIONS", [])
        if ext not in allowed:
            raise ValidationError("فرمت فایل مجاز نیست.")
        return file_name

    def clean_file_size(self):
        file_size = self.cleaned_data["file_size"]
        max_size = getattr(settings, "CHAT_MAX_ATTACHMENT_SIZE", 300 * 1024 * 1024)
        if file_size > max_size:
            raise ValidationError("حجم فایل بیشتر از حد مجاز است.")
        return file_size

    def clean_chunk(self):
        chunk = self.cleaned_data["chunk"]
        max_chunk_size = getattr(settings, "CHAT_UPLOAD_CHUNK_SIZE", 1024 * 1024)
        if chunk.size > max_chunk_size + 1024:
            raise ValidationError("اندازه تکه فایل معتبر نیست.")
        return chunk
