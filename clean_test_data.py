import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "painaima_core.settings")
django.setup()

from django.contrib.auth.models import User
from posts.models import Post, Story, Like, Comment, Bookmark, Tag
from accounts.models import Profile, Follow

def run_cleanup():
    print("[*] Starting data cleanup...")

    preserved_usernames = ["purachet", "admin"]
    preserved_emails = ["aunpu2588@gmail.com", "admin@painaima.local"]

    print("1. Deleting all posts, stories, bookmarks, comments, likes...")
    Like.objects.all().delete()
    Comment.objects.all().delete()
    Bookmark.objects.all().delete()
    Story.objects.all().delete()
    Post.objects.all().delete()
    Tag.objects.all().delete()
    Follow.objects.all().delete()
    print("   Posts and interactions cleared.")

    print("2. Cleaning test users...")
    test_users = User.objects.exclude(username__in=preserved_usernames).exclude(email__in=preserved_emails)
    deleted_count = test_users.count()
    deleted_names = list(test_users.values_list("username", flat=True))
    test_users.delete()
    print(f"   Deleted {deleted_count} test users: {deleted_names}")

    remaining_users = list(User.objects.values_list("username", "email"))
    print(f"[OK] Remaining active users: {remaining_users}")
    print("[SUCCESS] Cleanup completed successfully!")

if __name__ == "__main__":
    run_cleanup()
