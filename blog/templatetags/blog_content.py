from django import template
from django.utils.safestring import mark_safe

from blog.sanitizers import sanitize_blog_html


register = template.Library()


@register.filter
def render_blog_content(value):
    return mark_safe(sanitize_blog_html(value or ""))
