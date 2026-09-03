from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
    path("create/", views.post_create_view, name="post_create"),
    path("<int:pk>/", views.post_detail_view, name="post_detail"),
    path("<int:pk>/delete/", views.post_delete_view, name="post_delete"),
    path("<int:pk>/like/", views.like_toggle, name="like_toggle"),
    path("<int:pk>/bookmark/", views.bookmark_toggle, name="bookmark_toggle"),
    path("<int:pk>/comment/", views.add_comment, name="add_comment"),
    path("comment/<int:pk>/delete/", views.delete_comment, name="delete_comment"),
    path("tags/<str:tag_name>/", views.tag_posts_view, name="tag_posts"),
    path("location/<str:location_name>/", views.location_posts_view, name="location_posts"),
    path("<int:pk>/share-story/", views.share_to_story, name="share_to_story"),
    path("story/create/", views.story_create_view, name="story_create"),
    path("story/<int:story_id>/like/", views.story_like_toggle, name="story_like_toggle"),
    path("story/<int:story_id>/reply/", views.story_reply_api, name="story_reply_api"),
    path("story/<int:story_id>/delete/", views.story_delete_api, name="story_delete_api"),
    path("api/stories/<str:username>/", views.get_user_stories_api, name="get_user_stories_api"),
]
