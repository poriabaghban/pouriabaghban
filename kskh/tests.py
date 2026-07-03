import json

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import KskhPost
from .views import KSKH_DOWNLOAD_COOLDOWN_KEY, KSKH_SESSION_KEY, KSKH_USER_ID_KEY


class KskhLoginCsrfTests(TestCase):
    def setUp(self):
        get_user_model().objects.create_user(username="mobile-user", password="pass12345")
        self.client = Client(enforce_csrf_checks=True)

    def test_login_get_sets_csrf_cookie_and_post_does_not_403(self):
        login_url = reverse("kskh:login")
        response = self.client.get(
            login_url,
            secure=True,
            HTTP_HOST="pouriabaghban.ir",
            HTTP_X_FORWARDED_PROTO="https",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", self.client.cookies)

        csrf_token = self.client.cookies["csrftoken"].value
        response = self.client.post(
            login_url,
            {
                "username": "mobile-user",
                "password": "pass12345",
                "csrfmiddlewaretoken": csrf_token,
            },
            secure=True,
            HTTP_HOST="pouriabaghban.ir",
            HTTP_X_FORWARDED_PROTO="https",
            HTTP_REFERER=f"https://pouriabaghban.ir{login_url}",
        )

        self.assertNotEqual(response.status_code, 403)

    def test_mobile_subdomain_origin_is_trusted_behind_https_proxy(self):
        self.assertIn("https://*.pouriabaghban.ir", settings.CSRF_TRUSTED_ORIGINS)
        login_url = reverse("kskh:login")
        self.client.get(
            login_url,
            secure=True,
            HTTP_HOST="m.pouriabaghban.ir",
            HTTP_X_FORWARDED_PROTO="https",
        )
        csrf_token = self.client.cookies["csrftoken"].value

        response = self.client.post(
            login_url,
            {
                "username": "mobile-user",
                "password": "pass12345",
                "csrfmiddlewaretoken": csrf_token,
            },
            secure=True,
            HTTP_HOST="m.pouriabaghban.ir",
            HTTP_ORIGIN="https://m.pouriabaghban.ir",
            HTTP_REFERER=f"https://m.pouriabaghban.ir{login_url}",
            HTTP_X_FORWARDED_PROTO="https",
        )

        self.assertNotEqual(response.status_code, 403)

    def test_api_login_bypasses_csrf_and_returns_jwt_tokens(self):
        response = self.client.post(
            reverse("kskh:api_login"),
            data=json.dumps({"username": "mobile-user", "password": "pass12345"}),
            content_type="application/json",
            secure=True,
            HTTP_HOST="pouriabaghban.ir",
            HTTP_X_FORWARDED_PROTO="https",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertIn("access", payload)
        self.assertIn("refresh", payload)


class KskhDownloadFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="tester", password="pass")
        self.post = KskhPost.objects.create(
            title="Test Config",
            description="Test file",
            file=SimpleUploadedFile("test.ovpn", b"client\nremote example.com\n"),
            uploaded_by=self.user,
        )
        session = self.client.session
        session[KSKH_SESSION_KEY] = True
        session[KSKH_USER_ID_KEY] = self.user.pk
        session.save()

    def tearDown(self):
        if self.post.file:
            self.post.file.delete(save=False)

    def test_index_links_to_details_instead_of_direct_download(self):
        response = self.client.get(reverse("kskh:index"))

        self.assertContains(response, self.post.get_absolute_url())
        self.assertContains(response, f"{self.post.get_absolute_url()}?download=1")
        self.assertNotContains(response, reverse("kskh:download", args=[self.post.slug]))

    def test_detail_auto_download_flag_embeds_download_trigger(self):
        response = self.client.get(f"{reverse('kskh:detail', args=[self.post.slug])}?download=1")

        self.assertRedirects(response, reverse("kskh:download", args=[self.post.slug]), fetch_redirect_response=False)

    def test_direct_download_requires_opening_detail_first(self):
        response = self.client.get(reverse("kskh:download", args=[self.post.slug]))

        self.assertRedirects(response, reverse("kskh:detail", args=[self.post.slug]))
        self.post.refresh_from_db()
        self.assertEqual(self.post.download_count, 0)

    def test_download_cooldown_blocks_requests_for_seven_seconds(self):
        self.client.get(reverse("kskh:detail", args=[self.post.slug]))
        session = self.client.session
        session[KSKH_DOWNLOAD_COOLDOWN_KEY] = timezone.now().timestamp() - 3
        session.save()

        response = self.client.get(reverse("kskh:download", args=[self.post.slug]))

        self.assertRedirects(response, reverse("kskh:detail", args=[self.post.slug]))
        self.post.refresh_from_db()
        self.assertEqual(self.post.download_count, 0)
