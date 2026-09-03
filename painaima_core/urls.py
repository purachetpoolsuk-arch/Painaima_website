from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("u/", include("accounts.urls")),
    path("p/", include("posts.urls")),
    path("chat/", include("chat.urls")),
    path("", include("core.urls")),
]

from django.views.static import serve
from django.urls import re_path

urlpatterns += [
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT or settings.STATICFILES_DIRS[0]}),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
