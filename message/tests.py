from django.test import SimpleTestCase
from django.urls import reverse, resolve
from message.views import message_view   # ← اصلاح شد


class MessageViewTests(SimpleTestCase):

    def test_url_exists_at_correct_location(self):
        response = self.client.get('/message/')
        self.assertEqual(response.status_code, 200)

    def test_url_accessible_by_name(self):
        response = self.client.get(reverse('message'))
        self.assertEqual(response.status_code, 200)

    def test_url_resolves_to_correct_view(self):
        resolver = resolve('/message/')
        self.assertEqual(resolver.func, message_view)

    def test_template_used(self):
        response = self.client.get(reverse('message'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
