from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("edit/", views.edit_profile_view, name="edit_profile"),
    path("toggle-follow/<str:username>/", views.follow_toggle, name="toggle_follow"),
    path("<str:username>/connections/<str:conn_type>/", views.user_connections_api, name="user_connections_api"),
    path("demo-google-login/", views.demo_google_login, name="demo_google_login"),
    path("<str:username>/", views.profile_view, name="profile"),
]
