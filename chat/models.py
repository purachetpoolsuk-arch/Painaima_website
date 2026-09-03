from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    """Represents a chat conversation between users."""
    participants = models.ManyToManyField(User, related_name="conversations", verbose_name="ผู้ร่วมสนทนา")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="สร้างเมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="อัปเดตล่าสุด")

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "การสนทนา"
        verbose_name_plural = "การสนทนาทั้งหมด"

    def __str__(self):
        usernames = ", ".join(self.participants.values_list("username", flat=True))
        return f"Chat ({usernames})"

    def get_other_user(self, current_user):
        """Returns the other participant in a 1-on-1 conversation."""
        return self.participants.exclude(id=current_user.id).first()

    def get_last_message(self):
        """Returns the latest message in this conversation."""
        return self.messages.order_by("-created_at").first()

    def unread_count_for(self, user):
        """Returns count of unread messages for this user."""
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    """Represents a single message inside a conversation."""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages", verbose_name="ห้องสนทนา")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages", verbose_name="ผู้ส่ง")
    text = models.TextField(blank=True, verbose_name="ข้อความ")
    image = models.ImageField(upload_to="chat_images/%Y/%m/%d/", blank=True, null=True, verbose_name="รูปภาพแนบ")
    is_read = models.BooleanField(default=False, verbose_name="อ่านแล้ว")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="เวลาส่ง")

    class Meta:
        ordering = ["created_at"]
        verbose_name = "ข้อความ"
        verbose_name_plural = "ข้อความทั้งหมด"

    def __str__(self):
        return f"[{self.created_at.strftime('%H:%M')}] {self.sender.username}: {self.text[:30]}"
