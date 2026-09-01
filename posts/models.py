import re
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Tag(models.Model):
    name = models.CharField(max_length=60, unique=True, db_index=True, verbose_name="ชื่อแฮชแท็ก")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "แฮชแท็ก"
        verbose_name_plural = "แฮชแท็กทั้งหมด"

    def __str__(self):
        return f"#{self.name}"

    def get_absolute_url(self):
        return reverse("posts:tag_posts", kwargs={"tag_name": self.name})


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts", verbose_name="ผู้โพสต์")
    image = models.ImageField(upload_to="posts/%Y/%m/%d/", verbose_name="รูปภาพโพสต์")
    caption = models.TextField(blank=True, max_length=2200, verbose_name="แคปชั่น")
    location = models.CharField(max_length=200, blank=True, verbose_name="สถานที่ / เช็คอิน")
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts", verbose_name="แฮชแท็ก")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "โพสต์"
        verbose_name_plural = "โพสต์ทั้งหมด"

    def __str__(self):
        return f"Post #{self.id} by {self.author.username}"

    def get_absolute_url(self):
        return reverse("posts:post_detail", kwargs={"pk": self.pk})

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()

    def sync_tags(self):
        """Extracts #hashtags from the caption and saves tags to database."""
        # Find all hashtags (supports Thai, English, numbers, underscores)
        pattern = r"#([\w\u0E00-\u0E7F]+)"
        tag_names = set(re.findall(pattern, self.caption))
        
        tag_objects = []
        for name in tag_names:
            clean_name = name.strip()
            if clean_name:
                tag_obj, _ = Tag.objects.get_or_create(name=clean_name.lower())
                tag_objects.append(tag_obj)
        self.tags.set(tag_objects)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        self.sync_tags()


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes", verbose_name="ผู้กดไลก์")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes", verbose_name="โพสต์")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")
        ordering = ["-created_at"]
        verbose_name = "การกดไลก์"
        verbose_name_plural = "การกดไลก์ทั้งหมด"

    def __str__(self):
        return f"{self.user.username} liked Post #{self.post.id}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", verbose_name="ผู้คอมเมนต์")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="โพสต์")
    text = models.TextField(max_length=1000, verbose_name="ข้อความคอมเมนต์")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "ความคิดเห็น"
        verbose_name_plural = "ความคิดเห็นทั้งหมด"

    def __str__(self):
        return f"{self.user.username}: {self.text[:30]}"


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks", verbose_name="ผู้บันทึก")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="bookmarks", verbose_name="โพสต์")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")
        ordering = ["-created_at"]
        verbose_name = "โพสต์ที่บันทึก"
        verbose_name_plural = "โพสต์ที่บันทึกทั้งหมด"

    def __str__(self):
        return f"{self.user.username} saved Post #{self.post.id}"


class Story(models.Model):
    MEDIA_TYPE_CHOICES = [
        ("image", "รูปภาพ"),
        ("video", "วิดีโอ"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stories", verbose_name="เจ้าของสตอรี่")
    media_file = models.FileField(upload_to="stories/%Y/%m/%d/", blank=True, null=True, verbose_name="ไฟล์รูปภาพหรือวิดีโอสตอรี่")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default="image", verbose_name="ประเภทสื่อ")
    caption = models.CharField(max_length=255, blank=True, verbose_name="ข้อความสตอรี่")
    shared_post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True, related_name="shared_in_stories", verbose_name="โพสต์ที่แชร์มา")
    likes = models.ManyToManyField(User, related_name="liked_stories", blank=True, verbose_name="ผู้กดใจสตอรี่")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "สตอรี่"
        verbose_name_plural = "สตอรี่ทั้งหมด"

    def __str__(self):
        return f"Story #{self.id} ({self.media_type}) by {self.user.username}"

    @property
    def likes_count(self):
        return self.likes.count()


class StoryReply(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="replies", verbose_name="สตอรี่")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="story_replies", verbose_name="ผู้ตอบกลับ")
    text = models.TextField(max_length=500, verbose_name="ข้อความ")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "ข้อความตอบกลับสตอรี่"
        verbose_name_plural = "ข้อความตอบกลับสตอรี่ทั้งหมด"

    def __str__(self):
        return f"Reply by {self.user.username} on Story #{self.story.id}"


