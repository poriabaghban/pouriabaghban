from html import escape
from html.parser import HTMLParser
import re
from urllib.parse import urlsplit


ALLOWED_TAGS = {
    "a",
    "blockquote",
    "br",
    "code",
    "div",
    "em",
    "h2",
    "h3",
    "h4",
    "hr",
    "li",
    "ol",
    "p",
    "pre",
    "span",
    "strong",
    "ul",
}

ALLOWED_ATTRS = {
    "a": {"href", "title", "target", "rel"},
}

VOID_TAGS = {"br", "hr"}
SAFE_SCHEMES = {"http", "https", "mailto", "tel", ""}
URL_RE = re.compile(r"(?P<url>https?://[^\s<]+)")


def is_safe_link(value):
    value = (value or "").strip()
    if not value:
        return False
    parsed = urlsplit(value)
    return parsed.scheme.lower() in SAFE_SCHEMES


class SafeBlogHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.anchor_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag not in ALLOWED_TAGS:
            return

        clean_attrs = []
        allowed_attrs = ALLOWED_ATTRS.get(tag, set())
        for name, value in attrs:
            name = name.lower()
            if name not in allowed_attrs:
                continue
            if name == "href" and not is_safe_link(value):
                continue
            clean_attrs.append((name, value))

        if tag == "a" and any(name == "href" for name, _value in clean_attrs):
            attr_names = {name for name, _value in clean_attrs}
            if "target" in attr_names and "rel" not in attr_names:
                clean_attrs.append(("rel", "noopener noreferrer"))

        attrs_html = "".join(f' {name}="{escape(value or "", quote=True)}"' for name, value in clean_attrs)
        self.parts.append(f"<{tag}{attrs_html}>")
        if tag == "a":
            self.anchor_depth += 1

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in ALLOWED_TAGS and tag not in VOID_TAGS:
            self.parts.append(f"</{tag}>")
        if tag == "a" and self.anchor_depth:
            self.anchor_depth -= 1

    def handle_data(self, data):
        if self.anchor_depth:
            self.parts.append(escape(data))
            return
        last_end = 0
        for match in URL_RE.finditer(data):
            self.parts.append(escape(data[last_end:match.start()]))
            url = match.group("url").rstrip(".,;:!?)]}")
            trailing = match.group("url")[len(url):]
            safe_url = escape(url, quote=True)
            self.parts.append(
                f'<a href="{safe_url}" target="_blank" rel="noopener noreferrer">{escape(url)}</a>'
            )
            self.parts.append(escape(trailing))
            last_end = match.end()
        self.parts.append(escape(data[last_end:]))

    def handle_entityref(self, name):
        self.parts.append(f"&{name};")

    def handle_charref(self, name):
        self.parts.append(f"&#{name};")

    def get_html(self):
        return "".join(self.parts)


def sanitize_blog_html(value):
    if not value:
        return value
    parser = SafeBlogHTMLParser()
    parser.feed(value)
    parser.close()
    return parser.get_html()
