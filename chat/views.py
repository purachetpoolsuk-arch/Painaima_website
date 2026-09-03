from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Max, Q
from .models import Conversation, Message


@login_required
def inbox_view(request, conversation_id=None):
    """Main inbox & active conversation chat view."""
    # Get all conversations the current user is part of
    user_conversations = (
        request.user.conversations.annotate(latest_message_time=Max("messages__created_at"))
        .order_by("-latest_message_time", "-updated_at")
        .prefetch_related("participants", "participants__profile", "messages")
    )

    active_conversation = None
    messages_list = []
    other_user = None

    if conversation_id:
        active_conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in active_conversation.participants.all():
            return HttpResponseForbidden("You do not have access to this conversation.")

        # Mark unread messages sent by others as read
        active_conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

        other_user = active_conversation.get_other_user(request.user) or request.user
        messages_list = active_conversation.messages.select_related("sender", "sender__profile").all()
    elif user_conversations.exists():
        # Open first conversation by default on desktop if available
        first_conv = user_conversations.first()
        return redirect("chat:conversation", conversation_id=first_conv.id)

    # User suggestions to start a new chat with
    all_users = (
        User.objects.exclude(id=request.user.id)
        .select_related("profile")
        .order_by("-date_joined")[:15]
    )

    # Process conversation list data for display
    conversations_data = []
    for conv in user_conversations:
        conv_other = conv.get_other_user(request.user) or request.user
        last_msg = conv.get_last_message()
        unread = conv.unread_count_for(request.user)
        conversations_data.append({
            "id": conv.id,
            "other_user": conv_other,
            "last_message": last_msg,
            "unread_count": unread,
            "is_active": active_conversation and conv.id == active_conversation.id,
        })

    context = {
        "conversations": conversations_data,
        "active_conversation": active_conversation,
        "other_user": other_user,
        "messages_list": messages_list,
        "all_users": all_users,
    }
    return render(request, "chat/inbox.html", context)


@login_required
def start_chat_view(request, username):
    """Initiates a chat with a specific user and redirects to inbox."""
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return redirect("chat:inbox")

    # Look for existing conversation between these two users
    conversation = (
        Conversation.objects.filter(participants=request.user)
        .filter(participants=target_user)
        .first()
    )

    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, target_user)

    return redirect("chat:conversation", conversation_id=conversation.id)


@login_required
@require_POST
def api_send_message(request, conversation_id):
    """API to send a message via AJAX with optional image upload."""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user not in conversation.participants.all():
        return JsonResponse({"error": "Forbidden"}, status=403)

    text = request.POST.get("text", "").strip()
    image = request.FILES.get("image")

    if not text and not image:
        return JsonResponse({"error": "Cannot send empty message"}, status=400)

    msg = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        text=text,
        image=image,
    )
    # Touch conversation timestamp
    conversation.save(update_fields=["updated_at"])

    # If the user is chatting with admin and user is not admin, admin can auto-reply to simulate live conversation
    other_user = conversation.get_other_user(request.user)
    if other_user and other_user.username == "admin" and request.user.username != "admin":
        auto_replies = [
            f"สวัสดีครับคุณ {request.user.profile.display_name}! ยินดีต้อนรับสู่ Painaima (ไปไหนมา) ครับ 🌊✨",
            "ระบบแชทเชื่อมต่อกับ Neon Database และ Cloudinary เรียบร้อยแล้ว ข้อความทั้งหมดถูกบันทึกไว้อย่างถาวรครับ 🚀",
            "ขอบคุณที่ทดสอบระบบแชทนะครับ! มีสถานที่ท่องเที่ยวหรือคาเฟ่เด็ดๆ อย่าลืมแชร์ลงโพสต์และสตอรี่ด้วยนะค้าบ 📸",
        ]
        import random
        # Pick reply based on message count
        msg_count = conversation.messages.count()
        reply_idx = (msg_count // 2) % len(auto_replies)
        admin_reply_text = auto_replies[reply_idx]
        
        # Create admin reply
        Message.objects.create(
            conversation=conversation,
            sender=other_user,
            text=admin_reply_text,
        )
        conversation.save(update_fields=["updated_at"])

    return JsonResponse({
        "success": True,
        "message": {
            "id": msg.id,
            "sender_id": msg.sender.id,
            "sender_username": msg.sender.username,
            "sender_avatar": msg.sender.profile.avatar_url,
            "text": msg.text,
            "image_url": msg.image.url if msg.image else None,
            "created_at": msg.created_at.strftime("%H:%M"),
            "is_me": True,
        }
    })


@login_required
@require_GET
def api_get_messages(request, conversation_id):
    """API for real-time polling to fetch new messages."""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user not in conversation.participants.all():
        return JsonResponse({"error": "Forbidden"}, status=403)

    after_id = request.GET.get("after_id")
    query = conversation.messages.select_related("sender", "sender__profile")

    if after_id:
        try:
            query = query.filter(id__gt=int(after_id))
        except ValueError:
            pass

    # Mark incoming messages as read
    incoming = query.exclude(sender=request.user)
    incoming.filter(is_read=False).update(is_read=True)

    messages_data = [
        {
            "id": m.id,
            "sender_id": m.sender.id,
            "sender_username": m.sender.username,
            "sender_avatar": m.sender.profile.avatar_url,
            "text": m.text,
            "image_url": m.image.url if m.image else None,
            "created_at": m.created_at.strftime("%H:%M"),
            "is_me": m.sender == request.user,
        }
        for m in query
    ]

    return JsonResponse({
        "success": True,
        "messages": messages_data,
    })


@login_required
@require_GET
def api_unread_count(request):
    """API endpoint to get total unread messages count for navbar badge."""
    total_unread = Message.objects.filter(
        conversation__participants=request.user,
        is_read=False,
    ).exclude(sender=request.user).count()

    return JsonResponse({"unread_count": total_unread})
