import base64
import html
import os
import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

WIDTH, HEIGHT = 1080, 2340  # iPhone screen ratio (19.5:9)

_HERE = Path(__file__).resolve().parent
_FONTS_DIR = _HERE / "fonts"


def _font_b64(name: str) -> str:
    return base64.b64encode((_FONTS_DIR / name).read_bytes()).decode()


_TEMPLATE = (
    (_HERE / "card_template.html")
    .read_text()
    .replace("__CHIRP_B64__", _font_b64("Chirp.ttf"))
)

_TRAILING_HASHTAGS = re.compile(r"(?:\s*#\w+)+\s*$")
_HASHTAG = re.compile(r"#\w+")


def text_to_image(
    text_body: str,
    display_name: str | None = None,
    username: str | None = None,
    avatar: bytes | None = None,
    timestamp: int | None = None,
) -> bytes:
    """Render a message as a tweet-style 1080x1920 card and return PNG bytes."""
    body, hashtags = format_text(text_body)
    page_html = build_html(body, hashtags, display_name, username, avatar, timestamp)
    return render_png(page_html)


def format_text(text_body: str) -> tuple[str, str]:
    """Split trailing hashtags off the message body."""
    match = _TRAILING_HASHTAGS.search(text_body)
    if not match:
        return text_body.strip(), ""
    hashtags = " ".join(match.group().split())
    body = text_body[: match.start()].strip()
    return body, hashtags


def build_html(
    body: str,
    hashtags: str,
    display_name: str | None,
    username: str | None,
    avatar: bytes | None,
    timestamp: int | None,
) -> str:
    escaped = html.escape(body, quote=False)
    # color hashtags that appear inside the body text
    body_html = _HASHTAG.sub(lambda m: f'<span class="tag">{m.group()}</span>', escaped)

    name = display_name or username or "anonymous"

    if avatar is None:
        avatar_path = Path(os.getenv("AVATAR_PATH") or _HERE / "avatar.jpg")
        if avatar_path.is_file():
            avatar = avatar_path.read_bytes()

    if avatar:
        mime = "image/png" if avatar.startswith(b"\x89PNG") else "image/jpeg"
        avatar_b64 = base64.b64encode(avatar).decode()
        avatar_block = f'<img class="avatar" src="data:{mime};base64,{avatar_b64}">'
    else:
        initial = html.escape(name[0].upper(), quote=False)
        avatar_block = f'<div class="avatar avatar-fallback">{initial}</div>'

    handle_block = (
        f'<div class="handle">@{html.escape(username, quote=False)}</div>'
        if username
        else ""
    )

    hashtags_block = (
        f'<div class="hashtags">{html.escape(hashtags, quote=False)}</div>'
        if hashtags
        else ""
    )

    dt = datetime.fromtimestamp(timestamp) if timestamp else datetime.now()
    time_text = dt.strftime("%-I:%M %p · %b %-d, %Y")

    return (
        _TEMPLATE.replace("__FONT_SIZE__", str(font_size_for(body)))
        .replace("__AVATAR_BLOCK__", avatar_block)
        .replace("__NAME__", html.escape(name, quote=False))
        .replace("__HANDLE_BLOCK__", handle_block)
        .replace("__BODY__", body_html)
        .replace("__HASHTAGS_BLOCK__", hashtags_block)
        .replace("__TIMESTAMP__", time_text)
    )


def font_size_for(body: str) -> int:
    n = len(body)
    if n <= 90:
        return 62
    if n <= 180:
        return 54
    if n <= 320:
        return 46
    if n <= 500:
        return 40
    if n <= 900:
        return 34
    return 28


def render_png(page_html: str) -> bytes:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(
                viewport={"width": WIDTH, "height": HEIGHT},
                device_scale_factor=2,  # 2160x4680 output; layout unchanged
            )
            page.set_content(page_html, wait_until="networkidle")
            return page.screenshot(type="png")
        finally:
            browser.close()
