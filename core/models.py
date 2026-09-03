from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Notification(models.Model):
    TYPE_CHOICES = [
        ("like_post", "ถูกใจโพสต์ของคุณ"),
        ("comment_post", "แสดงความคิดเห็นบนโพสต์ของคุณ"),
        ("like_story", "ถูกใจสตอรี่ของคุณ"),
        ("reply_story", "ตอบกลับสตอรี่ของคุณ"),
        ("share_story", "แชร์โพสต์ของคุณลงในสตอรี่"),
        ("follow", "เริ่มติดตามคุณ"),
    ]

    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications_received", verbose_name="ผู้รับแจ้งเตือน"
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications_sent", verbose_name="ผู้กระทำการ"
    )
    notification_type = models.CharField(
        max_length=30, choices=TYPE_CHOICES, db_index=True, verbose_name="ประเภทการแจ้งเตือน"
    )
    post = models.ForeignKey(
        "posts.Post", on_delete=models.CASCADE, null=True, blank=True, related_name="notifications", verbose_name="โพสต์ที่เกี่ยวข้อง"
    )
    story = models.ForeignKey(
        "posts.Story", on_delete=models.CASCADE, null=True, blank=True, related_name="notifications", verbose_name="สตอรี่ที่เกี่ยวข้อง"
    )
    comment = models.ForeignKey(
        "posts.Comment", on_delete=models.CASCADE, null=True, blank=True, related_name="notifications", verbose_name="ความคิดเห็นที่เกี่ยวข้อง"
    )
    text_preview = models.CharField(max_length=255, blank=True, verbose_name="ข้อความตัวอย่าง")
    is_read = models.BooleanField(default=False, db_index=True, verbose_name="อ่านแล้วหรือยัง")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="เวลาที่สร้าง")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "การแจ้งเตือน"
        verbose_name_plural = "การแจ้งเตือนทั้งหมด"

    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username} ({self.notification_type})"

    def get_target_url(self):
        """Returns the appropriate URL to navigate to when clicking the notification."""
        if self.post:
            return self.post.get_absolute_url()
        elif self.notification_type == "reply_story":
            return f"/chat/u/{self.sender.username}/"
        elif self.notification_type in ("like_story", "share_story") and self.story:
            return f"/#story-{self.story.id}"
        return f"/u/{self.sender.username}/"


def create_notification(recipient, sender, notification_type, post=None, story=None, comment=None, text_preview=""):
    """Helper function to create a notification cleanly, preventing self-notifications."""
    if not recipient or not sender or recipient == sender:
        return None

    # Avoid duplicate unread notifications for the exact same action
    existing = Notification.objects.filter(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        post=post,
        story=story,
        is_read=False,
    ).first()
    if existing:
        existing.created_at = timezone.now()
        if text_preview:
            existing.text_preview = text_preview
        existing.save(update_fields=["created_at", "text_preview"] if text_preview else ["created_at"])
        return existing

    return Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        post=post,
        story=story,
        comment=comment,
        text_preview=text_preview,
    )
