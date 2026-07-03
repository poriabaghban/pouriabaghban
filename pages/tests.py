from django.test import Client, TestCase
from django.urls import reverse
from django.utils import translation

from .models import HomePageComment


class SubmitHomeCommentCsrfTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def test_home_comment_post_with_page_csrf_cookie_does_not_403(self):
        home_url = reverse("pages:home")
        response = self.client.get(
            home_url,
            secure=True,
            HTTP_HOST="pouriabaghban.ir",
            HTTP_X_FORWARDED_PROTO="https",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", self.client.cookies)

        csrf_token = self.client.cookies["csrftoken"].value
        response = self.client.post(
            reverse("pages:submit_home_comment"),
            {
                "name": "Mobile User",
                "email": "mobile@example.com",
                "comment": "Mobile comment",
                "csrfmiddlewaretoken": csrf_token,
            },
            secure=True,
            HTTP_HOST="pouriabaghban.ir",
            HTTP_X_FORWARDED_PROTO="https",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_REFERER="https://pouriabaghban.ir/",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(HomePageComment.objects.count(), 1)


class SubmitHomeCommentMessagesTests(TestCase):
    def post_comment(self):
        return self.client.post(
            reverse("pages:submit_home_comment"),
            {
                "name": "Test User",
                "email": "test@example.com",
                "comment": "A short comment",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

    def post_invalid_comment(self):
        return self.client.post(
            reverse("pages:submit_home_comment"),
            {
                "name": "Test User",
                "email": "test@example.com",
                "comment": "",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

    def test_submit_home_comment_messages_are_persian(self):
        with translation.override("fa"):
            success_response = self.post_comment()
            error_response = self.post_invalid_comment()

        self.assertEqual(success_response.status_code, 200)
        self.assertEqual(success_response.json()["message"], "نظر شما با موفقیت ارسال شد")
        self.assertEqual(error_response.status_code, 400)
        self.assertEqual(
            error_response.json()["message"],
            "متاسفانه نظر ارسال نشد مجددا تلاش فرمایید",
        )
        self.assertEqual(HomePageComment.objects.count(), 1)

    def test_submit_home_comment_messages_are_english(self):
        with translation.override("en"):
            success_response = self.post_comment()
            error_response = self.post_invalid_comment()

        self.assertEqual(success_response.status_code, 200)
        self.assertEqual(success_response.json()["message"], "Your comment was sent successfully.")
        self.assertEqual(error_response.status_code, 400)
        self.assertEqual(
            error_response.json()["message"],
            "Unfortunately, your comment was not sent. Please try again.",
        )

    def test_submit_home_comment_messages_are_german(self):
        with translation.override("de"):
            success_response = self.post_comment()
            error_response = self.post_invalid_comment()

        self.assertEqual(success_response.status_code, 200)
        self.assertEqual(
            success_response.json()["message"],
            "Ihr Kommentar wurde erfolgreich gesendet.",
        )
        self.assertEqual(error_response.status_code, 400)
        self.assertEqual(
            error_response.json()["message"],
            "Leider wurde Ihr Kommentar nicht gesendet. Bitte versuchen Sie es erneut.",
        )

    def test_submit_home_comment_rejects_forbidden_characters(self):
        response = self.client.post(
            reverse("pages:submit_home_comment"),
            {
                "name": "Test User",
                "email": "test@example.com",
                "comment": "bad < comment",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "استفاده از کاراکترهای % $ < > { } مجاز نیست.")
        self.assertEqual(HomePageComment.objects.count(), 0)
