import re
from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse

register = template.Library()


@register.filter(name="format_caption")
def format_caption(text):
    """Converts #hashtags and @mentions into clickable links."""
    if not text:
        return ""
    
    # Escape dangerous HTML first while preserving formatting
    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )

    # Convert hashtags #tag into links
    def replace_hashtag(match):
        tag = match.group(1)
        url = reverse("core:explore") + f"?q=%23{tag}"
        return f'<a href="{url}" class="hashtag-link font-semibold text-primary hover:underline">#{tag}</a>'

    # Convert @mentions into links
    def replace_mention(match):
        username = match.group(1)
        url = reverse("accounts:profile", kwargs={"username": username})
        return f'<a href="{url}" class="mention-link font-semibold text-accent hover:underline">@{username}</a>'

    # Pattern for hashtags (Thai & English characters)
    pattern_tag = r"#([\w\u0E00-\u0E7F]+)"
    pattern_mention = r"@([a-zA-Z0-9_]+)"

    result = re.sub(pattern_tag, replace_hashtag, escaped)
    result = re.sub(pattern_mention, replace_mention, result)

    # Convert newlines to <br>
    result = result.replace("\n", "<br>")
    return mark_safe(result)


@register.filter(name="has_liked")
def has_liked(post, user):
    """Checks if the user has liked the post."""
    if not user.is_authenticated:
        return False
    return post.likes.filter(user=user).exists()


@register.filter(name="has_bookmarked")
def has_bookmarked(post, user):
    """Checks if the user has bookmarked the post."""
    if not user.is_authenticated:
        return False
    return post.bookmarks.filter(user=user).exists()


@register.filter(name="is_following")
def is_following(target_user, current_user):
    """Checks if current_user is following target_user."""
    if not current_user.is_authenticated or target_user == current_user:
        return False
    return target_user.followers_set.filter(follower=current_user).exists()
