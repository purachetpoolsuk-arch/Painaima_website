from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "get_participants", "updated_at", "created_at")
    inlines = [MessageInline]

    def get_participants(self, obj):
        return ", ".join([u.username for u in obj.participants.all()])
    get_participants.short_description = "ผู้ร่วมสนทนา"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "text_preview", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("sender__username", "text")

    def text_preview(self, obj):
        return obj.text[:40] if obj.text else "[รูปภาพ]"
    text_preview.short_description = "ข้อความ"
