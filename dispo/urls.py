from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/create/", views.create_user),
    path("post/create/", views.create_post),
    path("post/like/", views.like_post),
    path("users/top/", views.get_users),
    path("users/follow/", views.follow_user),
    path("users/feed/<int:user_id>/", views.get_user_feed),
]
