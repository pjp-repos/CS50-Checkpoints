
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API Routes
    
    # Create a new post
    path("newpost", views.new_post, name="new_post"),
    # Edit an existing post
    path("editpost/<int:post_id>", views.edit_post, name="edit_post"),
    # Get an individual post
    path("post/<int:post_id>", views.view_post, name="view_post"),
    # Get a list of posts filered by any criteria
    path("posts/<str:list>", views.posts_list, name="posts_list"),
    # Follow lists
    path("followlist", views.follow_list, name="follow_list"),
    # Follow counts
    path("followcounts", views.follow_counts, name="follow_counts"),
    # Follow/Unfollow users
    path("follow", views.follow, name="follow"),
    # Like posts
    path("like/<int:post_id>", views.like, name="like"),

]
