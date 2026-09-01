from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.feed_view, name="feed"),
    path("explore/", views.explore_view, name="explore"),
    path("api/search/", views.search_api, name="search_api"),
]
