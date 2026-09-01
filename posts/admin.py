from django.contrib import admin
from .models import Post, Tag, Like, Comment, Bookmark, Story


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "caption", "created_at")
    search_fields = ("user__username", "caption")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "location", "likes_count", "comments_count", "created_at")
    list_filter = ("created_at", "tags")
    search_fields = ("caption", "location", "author__username")
    filter_horizontal = ("tags",)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")
    search_fields = ("user__username",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "text", "created_at")
    search_fields = ("user__username", "text")


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")
    search_fields = ("user__username",)
