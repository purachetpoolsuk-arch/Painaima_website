from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.inbox_view, name="inbox"),
    path("<int:conversation_id>/", views.inbox_view, name="conversation"),
    path("with/<str:username>/", views.start_chat_view, name="start_chat"),
    path("api/<int:conversation_id>/send/", views.api_send_message, name="api_send"),
    path("api/<int:conversation_id>/messages/", views.api_get_messages, name="api_messages"),
    path("api/unread-count/", views.api_unread_count, name="api_unread_count"),
]
