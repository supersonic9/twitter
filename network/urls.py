
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("edit", views.edit, name="edit"),
    path("following", views.following, name="following"),
    path("like", views.like, name="like"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("profile/<int:profile_id>", views.profile, name="profile"),
    path("profile/like", views.like, name="like"),
    path("profile/unlike", views.unlike, name="unlike"),
    path("register", views.register, name="register"),
    path("unlike", views.unlike, name="unlike")
]
