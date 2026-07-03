from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import BlogComment, BlogPost


class BlogCommentPublishingTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pass")
        self.post = BlogPost.objects.create(
            title="Legacy title",
            title_fa="عنوان تست",
            slug="test-post",
            author=self.author,
            content="Legacy content",
            content_fa="متن تست",
            excerpt="Legacy excerpt",
            excerpt_fa="خلاصه تست",
            status="published",
            is_active=True,
        )

    def test_new_comment_is_published_immediately(self):
        response = self.client.post(
            reverse("blog:post-detail", kwargs={"slug": self.post.slug}),
            {"name": "Ali", "email": "ali@example.com", "content": "Nice post"},
        )

        self.assertRedirects(response, reverse("blog:post-detail", kwargs={"slug": self.post.slug}))
        comment = BlogComment.objects.get(author="Ali")
        self.assertTrue(comment.is_approved)
        self.assertIsNone(comment.parent)

    def test_reply_is_published_immediately(self):
        approved_comment = BlogComment.objects.create(
            post=self.post,
            author="Sara",
            email="sara@example.com",
            content="Approved comment",
            is_approved=True,
        )

        response = self.client.post(
            reverse("blog:post-detail", kwargs={"slug": self.post.slug}),
            {
                "reply_to": str(approved_comment.id),
                "name": "Reza",
                "email": "reza@example.com",
                "content": "Reply content",
            },
        )

        self.assertRedirects(response, reverse("blog:post-detail", kwargs={"slug": self.post.slug}))
        reply = BlogComment.objects.get(author="Reza")
        self.assertEqual(reply.parent, approved_comment)
        self.assertTrue(reply.is_approved)

    def test_comment_rejects_forbidden_characters(self):
        response = self.client.post(
            reverse("blog:post-detail", kwargs={"slug": self.post.slug}),
            {"name": "Ali", "email": "ali@example.com", "content": "Nice < post"},
        )

        self.assertRedirects(response, reverse("blog:post-detail", kwargs={"slug": self.post.slug}))
        self.assertFalse(BlogComment.objects.filter(author="Ali").exists())
