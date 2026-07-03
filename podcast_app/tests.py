import hashlib

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import PodcastAdminForm
from .models import Podcast


class PodcastAdminFormTests(TestCase):
    def test_duplicate_audio_content_is_rejected(self):
        audio_content = b"same audio bytes"
        existing = Podcast.objects.create(
            title="first poem",
            speaker="poet",
            description="description",
        )
        Podcast.objects.filter(pk=existing.pk).update(
            audio_file_sha256=hashlib.sha256(audio_content).hexdigest()
        )

        form = PodcastAdminForm(
            data={
                "title": "second poem",
                "speaker": "poet",
                "description": "description",
                "transcript": "",
                "duration": "",
                "is_published": "on",
                "category": "",
            },
            files={
                "audio_file": SimpleUploadedFile(
                    "second-name.mp3",
                    audio_content,
                    content_type="audio/mpeg",
                )
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("audio_file", form.errors)


class PodcastAccessTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="listener",
            password="strong-test-password",
        )
        self.regular = Podcast.objects.create(
            title="regular poem",
            speaker="poet",
            description="description",
            content_type=Podcast.CONTENT_REGULAR,
        )
        self.special = Podcast.objects.create(
            title="special poem",
            speaker="poet",
            description="description",
            content_type=Podcast.CONTENT_SPECIAL,
        )

    def test_regular_list_hides_special_poems(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("podcast_app:sheer_list"))

        self.assertContains(response, self.regular.title)
        self.assertNotContains(response, self.special.title)

    def test_special_page_requires_separate_login_flag(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("podcast_app:special_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/sheerwizhe/login/", response["Location"])

        session = self.client.session
        session["sheerwizhe_authenticated"] = True
        session.save()

        response = self.client.get(reverse("podcast_app:special_list"))
        self.assertContains(response, self.special.title)
        self.assertNotContains(response, self.regular.title)

