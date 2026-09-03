from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.feed_view, name="feed"),
    path("explore/", views.explore_view, name="explore"),
    path("notifications/", views.notifications_view, name="notifications"),
    path("api/search/", views.search_api, name="search_api"),
    path("api/notifications/", views.api_get_notifications, name="api_notifications"),
    path("api/notifications/mark-read/", views.api_mark_notifications_read, name="api_mark_notifications_read"),
    path("api/notifications/unread-count/", views.api_unread_notifications_count, name="api_unread_notifications_count"),
]
