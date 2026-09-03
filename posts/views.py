from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .models import Post, Tag, Like, Comment, Bookmark, Story
from .forms import PostCreateForm, CommentForm
from core.models import create_notification


@login_required
def post_create_view(request):
    if request.method == "POST":
        form = PostCreateForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # sync_tags is called on save()
            messages.success(request, "สร้างโพสต์เรียบร้อยแล้ว!")
            return redirect("posts:post_detail", pk=post.pk)
    else:
        form = PostCreateForm()
    
    return render(request, "posts/post_create.html", {"form": form})


def post_detail_view(request, pk):
    post = get_object_or_404(
        Post.objects.select_related("author", "author__profile").prefetch_related("tags", "comments__user__profile"),
        pk=pk
    )
    comment_form = CommentForm()
    
    # Check if user liked/bookmarked
    user_has_liked = False
    user_has_bookmarked = False
    if request.user.is_authenticated:
        user_has_liked = post.likes.filter(user=request.user).exists()
        user_has_bookmarked = post.bookmarks.filter(user=request.user).exists()

    context = {
        "post": post,
        "comments": post.comments.all().order_by("created_at"),
        "comment_form": comment_form,
        "user_has_liked": user_has_liked,
        "user_has_bookmarked": user_has_bookmarked,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
@require_POST
def post_delete_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์ลบโพสต์นี้")
    
    post.delete()
    messages.success(request, "ลบโพสต์เรียบร้อยแล้ว")
    return redirect("accounts:profile", username=request.user.username)


@login_required
@require_POST
def like_toggle(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like_obj = Like.objects.filter(user=request.user, post=post)
    
    if like_obj.exists():
        like_obj.delete()
        liked = False
    else:
        Like.objects.create(user=request.user, post=post)
        liked = True
        create_notification(post.author, request.user, "like_post", post=post)

    return JsonResponse({
        "success": True,
        "liked": liked,
        "likes_count": post.likes.count(),
    })


@login_required
@require_POST
def bookmark_toggle(request, pk):
    post = get_object_or_404(Post, pk=pk)
    bookmark_obj = Bookmark.objects.filter(user=request.user, post=post)
    
    if bookmark_obj.exists():
        bookmark_obj.delete()
        bookmarked = False
        message = "นำออกจากรายการที่บันทึกแล้ว"
    else:
        Bookmark.objects.create(user=request.user, post=post)
        bookmarked = True
        message = "บันทึกโพสต์แล้ว"

    return JsonResponse({
        "success": True,
        "bookmarked": bookmarked,
        "message": message,
    })


@login_required
@require_POST
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.post = post
        comment.save()

        # Send notification to post author
        create_notification(
            post.author, request.user, "comment_post", post=post, comment=comment, text_preview=comment.text[:120]
        )

        # If AJAX request
        if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("is_ajax"):
            return JsonResponse({
                "success": True,
                "comment": {
                    "id": comment.id,
                    "user": comment.user.username,
                    "display_name": comment.user.profile.display_name,
                    "avatar_url": comment.user.profile.avatar_url,
                    "text": comment.text,
                    "created_at": "เมื่อสักครู่",
                },
                "comments_count": post.comments.count(),
            })

        messages.success(request, "เพิ่มความคิดเห็นแล้ว")
        return redirect("posts:post_detail", pk=pk)
    
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"success": False, "errors": form.errors}, status=400)
    
    return redirect("posts:post_detail", pk=pk)


@login_required
@require_POST
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user != request.user and comment.post.author != request.user:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์ลบคอมเมนต์นี้")
    
    post = comment.post
    comment.delete()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "comments_count": post.comments.count(),
        })

    messages.success(request, "ลบความคิดเห็นแล้ว")
    return redirect("posts:post_detail", pk=post.pk)


def tag_posts_view(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name.lower())
    posts = tag.posts.all().select_related("author", "author__profile").prefetch_related("likes", "comments")
    context = {
        "tag": tag,
        "posts": posts,
        "posts_count": posts.count(),
    }
    return render(request, "posts/tag_posts.html", context)


def location_posts_view(request, location_name):
    posts = Post.objects.filter(location__iexact=location_name).select_related("author", "author__profile").prefetch_related("likes", "comments")
    context = {
        "location_name": location_name,
        "posts": posts,
        "posts_count": posts.count(),
    }
    return render(request, "posts/location_posts.html", context)


@login_required
@require_POST
def share_to_story(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Create a new story from the shared post
    story = Story.objects.create(
        user=request.user,
        media_file=post.image,
        media_type="image",
        caption=f"แชร์โพสต์ของ @{post.author.username}: {post.caption[:60]}",
        shared_post=post,
    )

    # Send notification to post author
    create_notification(post.author, request.user, "share_story", post=post, story=story)

    return JsonResponse({
        "success": True,
        "message": "แชร์ลงสตอรี่ของคุณเรียบร้อยแล้ว!",
        "story_id": story.id,
    })


@login_required
@require_POST
def story_create_view(request):
    media = request.FILES.get("media_file")
    caption = request.POST.get("caption", "").strip()

    if not media:
        if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("is_ajax"):
            return JsonResponse({"success": False, "error": "กรุณาเลือกรูปภาพหรือวิดีโอ"}, status=400)
        messages.error(request, "กรุณาเลือกรูปภาพหรือวิดีโอ")
        return redirect("core:feed")

    # Detect if media is video
    content_type = getattr(media, "content_type", "")
    filename = media.name.lower()
    if content_type.startswith("video") or filename.endswith((".mp4", ".webm", ".mov", ".mkv")):
        media_type = "video"
    else:
        media_type = "image"

    story = Story.objects.create(
        user=request.user,
        media_file=media,
        media_type=media_type,
        caption=caption,
    )

    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("is_ajax"):
        return JsonResponse({
            "success": True,
            "message": "ลงสตอรี่สำเร็จแล้ว! 🎉",
            "story": {
                "id": story.id,
                "media_url": story.media_file.url,
                "media_type": story.media_type,
                "caption": story.caption,
            }
        })

    messages.success(request, "ลงสตอรี่สำเร็จแล้ว! 🎉")
    return redirect("core:feed")


@login_required
@require_POST
def story_like_toggle(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    if request.user in story.likes.all():
        story.likes.remove(request.user)
        liked = False
    else:
        story.likes.add(request.user)
        liked = True
        create_notification(story.user, request.user, "like_story", story=story)

    return JsonResponse({
        "success": True,
        "liked": liked,
        "likes_count": story.likes.count(),
    })


@login_required
@require_POST
def story_reply_api(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    text = request.POST.get("text", "").strip()
    
    if not text:
        return JsonResponse({"success": False, "error": "ข้อความว่างเปล่า"}, status=400)

    from .models import StoryReply
    reply = StoryReply.objects.create(
        story=story,
        user=request.user,
        text=text,
    )

    create_notification(
        story.user, request.user, "reply_story", story=story, text_preview=reply.text[:120]
    )

    return JsonResponse({
        "success": True,
        "message": f"ส่งข้อความหา @{story.user.username} แล้ว",
        "reply": {
            "id": reply.id,
            "sender": request.user.username,
            "text": reply.text,
        }
    })


@login_required
def get_user_stories_api(request, username):
    user_obj = get_object_or_404(User, username=username)
    stories = Story.objects.filter(user=user_obj).order_by("created_at")
    
    data = [
        {
            "id": s.id,
            "media_url": s.media_file.url if s.media_file else "",
            "media_type": s.media_type,
            "caption": s.caption,
            "created_at": s.created_at.strftime("%H:%M น."),
            "likes_count": s.likes.count(),
            "has_liked": request.user in s.likes.all(),
            "shared_post_url": s.shared_post.get_absolute_url() if s.shared_post else "",
        }
        for s in stories
    ]

    return JsonResponse({
        "user": {
            "username": user_obj.username,
            "display_name": user_obj.profile.display_name,
            "avatar_url": user_obj.profile.avatar_url,
            "is_self": request.user == user_obj,
        },
        "stories": data,
    })


