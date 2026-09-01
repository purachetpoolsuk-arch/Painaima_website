from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=150, blank=True, verbose_name="ชื่อ-นามสกุล / ชื่อที่แสดง")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="รูปโปรไฟล์")
    bio = models.TextField(max_length=500, blank=True, verbose_name="คำอธิบายตัวเอง (Bio)")
    location = models.CharField(max_length=120, blank=True, verbose_name="ที่อยู่ / เมือง")
    website = models.URLField(blank=True, verbose_name="เว็บไซต์หรือลิงก์")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    @property
    def display_name(self):
        return self.full_name.strip() if self.full_name else self.user.username

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        # Modern avatar fallback with user initials
        name = self.user.username
        return f"https://api.dicebear.com/7.x/notionists/svg?seed={name}&backgroundColor=b6e3f4,c0aede,d1d4f9,ffd5dc,ffdfbf"

    @property
    def followers_count(self):
        return self.user.followers_set.count()

    @property
    def following_count(self):
        return self.user.following_set.count()

    @property
    def posts_count(self):
        return self.user.posts.count()


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_set", verbose_name="ผู้ติดตาม")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers_set", verbose_name="คนที่กำลังติดตาม")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")
        ordering = ["-created_at"]
        verbose_name = "การติดตาม"
        verbose_name_plural = "การติดตามทั้งหมด"

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
    else:
        if hasattr(instance, "profile"):
            instance.profile.save()
