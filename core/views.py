from django.shortcuts import render
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from posts.models import Post, Tag, Story
from accounts.models import Follow


@login_required
def feed_view(request):
    # Get users that current user is following
    following_ids = list(request.user.following_set.values_list("following_id", flat=True))
    feed_user_ids = following_ids + [request.user.id]

    posts = Post.objects.filter(author_id__in=feed_user_ids).select_related(
        "author", "author__profile"
    ).prefetch_related("tags", "likes", "comments", "comments__user", "comments__user__profile")

    # If user has no or very few following posts, show recent discovery posts
    if posts.count() < 3:
        discovery_posts = Post.objects.exclude(id__in=posts.values_list("id", flat=True)).select_related(
            "author", "author__profile"
        ).prefetch_related("tags", "likes", "comments", "comments__user")[:15]
        feed_is_mixed = True
    else:
        discovery_posts = None
        feed_is_mixed = False

    # Suggested users to follow (excluding self and already followed users)
    exclude_users = following_ids + [request.user.id]
    suggested_users = User.objects.exclude(id__in=exclude_users).select_related("profile")[:5]

    # Users who have stories
    story_users = User.objects.filter(stories__isnull=False).distinct().select_related("profile")

    # Trending tags
    trending_tags = Tag.objects.annotate(num_posts=Count("posts")).order_by("-num_posts")[:8]
    
    # Popular locations
    popular_locations = (
        Post.objects.exclude(location="")
        .values("location")
        .annotate(total=Count("id"))
        .order_by("-total")[:6]
    )

    user_has_story = request.user.stories.exists()

    context = {
        "posts": posts,
        "discovery_posts": discovery_posts,
        "feed_is_mixed": feed_is_mixed,
        "suggested_users": suggested_users,
        "story_users": story_users,
        "user_has_story": user_has_story,
        "trending_tags": trending_tags,
        "popular_locations": popular_locations,
    }
    return render(request, "core/feed.html", context)


@login_required
def explore_view(request):
    query = request.GET.get("q", "").strip()
    tag_filter = request.GET.get("tag", "").strip()
    location_filter = request.GET.get("location", "").strip()

    posts = Post.objects.all().select_related("author", "author__profile").prefetch_related("likes", "comments")
    users_matched = []

    if query:
        if query.startswith("#"):
            clean_tag = query.lstrip("#")
            posts = posts.filter(tags__name__icontains=clean_tag)
        else:
            users_matched = User.objects.filter(
                Q(username__icontains=query) | Q(profile__full_name__icontains=query)
            ).select_related("profile")[:6]
            posts = posts.filter(
                Q(caption__icontains=query) |
                Q(location__icontains=query) |
                Q(tags__name__icontains=query) |
                Q(author__username__icontains=query)
            ).distinct()
    elif tag_filter:
        posts = posts.filter(tags__name__iexact=tag_filter)
    elif location_filter:
        posts = posts.filter(location__icontains=location_filter)

    trending_tags = Tag.objects.annotate(num_posts=Count("posts")).order_by("-num_posts")[:12]
    popular_locations = (
        Post.objects.exclude(location="")
        .values("location")
        .annotate(total=Count("id"))
        .order_by("-total")[:8]
    )

    context = {
        "query": query,
        "tag_filter": tag_filter,
        "location_filter": location_filter,
        "posts": posts,
        "users_matched": users_matched,
        "trending_tags": trending_tags,
        "popular_locations": popular_locations,
    }
    return render(request, "core/explore.html", context)


def search_api(request):
    """Real-time autocomplete search endpoint."""
    q = request.GET.get("q", "").strip()
    if not q or len(q) < 1:
        return JsonResponse({"users": [], "tags": [], "locations": []})

    clean_tag = q.lstrip("#")
    
    users = [
        {
            "username": u.username,
            "display_name": u.profile.display_name,
            "avatar_url": u.profile.avatar_url,
            "url": f"/u/{u.username}/",
        }
        for u in User.objects.filter(
            Q(username__icontains=q) | Q(profile__full_name__icontains=q)
        ).select_related("profile")[:4]
    ]

    tags = [
        {
            "name": t.name,
            "posts_count": t.posts.count(),
            "url": f"/explore/?q=%23{t.name}",
        }
        for t in Tag.objects.filter(name__icontains=clean_tag)[:4]
    ]

    locations = [
        {
            "name": item["location"],
            "count": item["count"],
            "url": f"/explore/?location={item['location']}",
        }
        for item in (
            Post.objects.filter(location__icontains=q)
            .values("location")
            .annotate(count=Count("id"))[:4]
        )
    ]

    return JsonResponse({
        "users": users,
        "tags": tags,
        "locations": locations,
    })
