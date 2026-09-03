from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Profile, Follow
from .forms import ProfileEditForm, UserEditForm
from posts.models import Post, Like, Bookmark
from core.models import create_notification


@login_required
def profile_view(request, username):
    user_obj = get_object_or_404(User, username=username)
    profile = user_obj.profile

    # Active tab: 'posts' (default), 'saved', 'liked'
    tab = request.GET.get("tab", "posts")
    
    # Query posts depending on tab
    if tab == "saved":
        if request.user.is_authenticated and request.user == user_obj:
            bookmarked_ids = Bookmark.objects.filter(user=user_obj).values_list("post_id", flat=True)
            posts = Post.objects.filter(id__in=bookmarked_ids).select_related("author", "author__profile").prefetch_related("likes", "comments")
        else:
            posts = Post.objects.none()
    elif tab == "liked":
        if request.user.is_authenticated and request.user == user_obj:
            liked_ids = Like.objects.filter(user=user_obj).values_list("post_id", flat=True)
            posts = Post.objects.filter(id__in=liked_ids).select_related("author", "author__profile").prefetch_related("likes", "comments")
        else:
            posts = Post.objects.none()
    else:
        posts = user_obj.posts.all().select_related("author", "author__profile").prefetch_related("likes", "comments")

    is_following = False
    if request.user.is_authenticated and request.user != user_obj:
        is_following = Follow.objects.filter(follower=request.user, following=user_obj).exists()

    context = {
        "profile_user": user_obj,
        "profile": profile,
        "posts": posts,
        "active_tab": tab,
        "is_following": is_following,
        "is_own_profile": request.user == user_obj,
        "followers_count": user_obj.followers_set.count(),
        "following_count": user_obj.following_set.count(),
        "posts_count": user_obj.posts.count(),
    }
    return render(request, "accounts/profile.html", context)


@login_required
def edit_profile_view(request):
    profile = request.user.profile
    if request.method == "POST":
        u_form = UserEditForm(request.POST, instance=request.user)
        p_form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "อัปเดตข้อมูลโปรไฟล์เรียบร้อยแล้ว!")
            return redirect("accounts:profile", username=request.user.username)
    else:
        u_form = UserEditForm(instance=request.user)
        p_form = ProfileEditForm(instance=profile)

    return render(request, "accounts/edit_profile.html", {"u_form": u_form, "p_form": p_form})


@login_required
@require_POST
def follow_toggle(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return JsonResponse({"error": "You cannot follow yourself"}, status=400)

    follow_obj = Follow.objects.filter(follower=request.user, following=target_user)
    if follow_obj.exists():
        follow_obj.delete()
        is_following = False
        message = f"เลิกติดตาม @{target_user.username} แล้ว"
    else:
        Follow.objects.create(follower=request.user, following=target_user)
        is_following = True
        message = f"กำลังติดตาม @{target_user.username}"
        create_notification(target_user, request.user, "follow")

    return JsonResponse({
        "success": True,
        "is_following": is_following,
        "followers_count": target_user.followers_set.count(),
        "message": message,
    })


def user_connections_api(request, username, conn_type):
    user_obj = get_object_or_404(User, username=username)
    if conn_type == "followers":
        users = [f.follower for f in user_obj.followers_set.select_related("follower__profile").all()]
        title = "ผู้ติดตาม (Followers)"
    elif conn_type == "following":
        users = [f.following for f in user_obj.following_set.select_related("following__profile").all()]
        title = "กำลังติดตาม (Following)"
    else:
        return JsonResponse({"error": "Invalid connection type"}, status=400)

    data = [
        {
            "username": u.username,
            "display_name": u.profile.display_name,
            "avatar_url": u.profile.avatar_url,
            "profile_url": u.profile.get_absolute_url if hasattr(u.profile, "get_absolute_url") else f"/u/{u.username}/",
            "is_following": request.user.is_authenticated and Follow.objects.filter(follower=request.user, following=u).exists() if request.user != u else None,
            "is_self": request.user == u,
        }
        for u in users
    ]
    return JsonResponse({"title": title, "users": data})


def demo_google_login(request):
    import os
    from django.contrib.auth import login
    
    google_client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    
    # If real Google Client ID is configured, forward to allauth Google OAuth
    if google_client_id:
        return redirect("/accounts/google/login/?process=login")
    
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        name = request.POST.get("name", "").strip()
        
        if not email:
            email = "aunpu2588@gmail.com"
        if not name:
            name = email.split("@")[0].capitalize()
            
        username = email.split("@")[0].replace(".", "_") + "_google"
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": name,
            }
        )
        if created:
            user.set_password("GoogleAuthPass2026!")
            user.save()
            user.profile.full_name = f"{name} (Google)"
            user.profile.bio = f"เชื่อมต่อผ่านบัญชี Google ({email}) ✨"
            user.profile.save()
            
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, f"เข้าสู่ระบบด้วย Google ({user.email}) สำเร็จแล้ว! 🎉")
        return redirect("core:feed")
        
    return render(request, "socialaccount/google_chooser.html")



