from html.parser import HTMLParser
import re
from urllib.parse import urljoin, urlparse


URL_ATTRS = {"href", "src", "action"}
IGNORED_SCHEMES = {"", "http"}
SKIPPED_PREFIXES = ("#", "mailto:", "tel:", "javascript:", "data:")
QUOTED_ASSET_PATTERN = re.compile(r"""(?P<quote>["'])(?P<url>(?![a-z][a-z0-9+.-]*:|//|/|#)[^"']+\.(?:css|js|png|jpe?g|gif|svg|webp|ico|woff2?|ttf|eot)(?:\?[^"']*)?)(?P=quote)""", re.IGNORECASE)
CSS_URL_PATTERN = re.compile(r"""url\((?P<quote>["']?)(?P<url>(?![a-z][a-z0-9+.-]*:|//|/|#)[^"')]+)(?P=quote)\)""", re.IGNORECASE)


class HtmlAssetRewriter(HTMLParser):
    def __init__(self, base_url: str, proxy_base_url: str):
        super().__init__(convert_charrefs=False)
        self.base_url = base_url
        self.proxy_base_url = proxy_base_url.rstrip("/")
        self.proxied_base_url = _proxied_url(_ensure_trailing_slash(base_url), base_url, self.proxy_base_url)
        self.inserted_base = False
        self.parts: list[str] = []

    def rewrite(self, html: str) -> str:
        self.parts = []
        self.feed(html)
        self.close()
        return "".join(self.parts)

    def handle_decl(self, decl: str) -> None:
        self.parts.append(f"<!{decl}>")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.parts.append(self._render_tag(tag, attrs, closed=False))
        if tag.lower() == "head" and not self.inserted_base:
            self.parts.append(f'<base href="{_escape_attr(self.proxied_base_url)}">')
            self.inserted_base = True

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.parts.append(self._render_tag(tag, attrs, closed=True))

    def handle_endtag(self, tag: str) -> None:
        self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.parts.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        self.parts.append(f"<!--{data}-->")

    def _render_tag(self, tag: str, attrs: list[tuple[str, str | None]], closed: bool) -> str:
        rendered_attrs = []
        for name, value in attrs:
            if value is None:
                rendered_attrs.append(name)
                continue

            rendered_value = self._rewrite_attr(name, value)
            rendered_attrs.append(f'{name}="{_escape_attr(rendered_value)}"')

        attrs_text = f" {' '.join(rendered_attrs)}" if rendered_attrs else ""
        suffix = " />" if closed else ">"
        return f"<{tag}{attrs_text}{suffix}"

    def _rewrite_attr(self, name: str, value: str) -> str:
        if name.lower() not in URL_ATTRS or _should_skip_url(value):
            return value

        absolute_url = urljoin(self.base_url, value)
        parsed = urlparse(absolute_url)
        if parsed.scheme not in IGNORED_SCHEMES or not parsed.netloc:
            return value

        return _proxied_url(value, self.base_url, self.proxy_base_url)


def rewrite_asset_urls(html: str, base_url: str, proxy_base_url: str) -> str:
    return HtmlAssetRewriter(base_url, proxy_base_url).rewrite(html)


def rewrite_embedded_asset_urls(content: str, base_url: str, proxy_base_url: str) -> str:
    proxy_base_url = proxy_base_url.rstrip("/")

    def replace_quoted(match: re.Match[str]) -> str:
        quote = match.group("quote")
        url = match.group("url")
        return f"{quote}{_proxied_url(url, base_url, proxy_base_url)}{quote}"

    def replace_css_url(match: re.Match[str]) -> str:
        quote = match.group("quote")
        url = match.group("url")
        return f"url({quote}{_proxied_url(url, base_url, proxy_base_url)}{quote})"

    rewritten = QUOTED_ASSET_PATTERN.sub(replace_quoted, content)
    return CSS_URL_PATTERN.sub(replace_css_url, rewritten)


def _should_skip_url(value: str) -> bool:
    normalized = value.strip().lower()
    return not normalized or normalized.startswith(SKIPPED_PREFIXES)


def _proxied_url(url: str, base_url: str, proxy_base_url: str) -> str:
    absolute_url = urljoin(base_url, url)
    parsed = urlparse(absolute_url)
    if parsed.scheme != "http" or not parsed.netloc:
        return url
    if not proxy_base_url:
        return absolute_url
    return f"{proxy_base_url}/{absolute_url}"


def _escape_attr(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _ensure_trailing_slash(url: str) -> str:
    parsed = urlparse(url)
    if parsed.path and not parsed.path.endswith("/"):
        return urljoin(url, ".")
    if not url.endswith("/"):
        return f"{url}/"
    return url
