
from django.urls import path

from . import views

app_name = "network"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),


    path("posts", views.all_posts, name="allposts"),

    path("create_post", views.create_post, name="create"),
    path('profile/<str:username>', views.user_profile_view, name='profile'),
    path('follow_profile/',views.follow_profile, name='follow_profile'),
    path('following/', views.following_posts, name="following"),

    path("edit/<int:post_id>", views.edit_post, name="edit"),

    path('like/<int:post_id>/', views.like_post, name='like_post'),



]
'''path('follow_toggle/', views.follow_toggle, name='follow_toggle'),'''

'''path('following/<str:created_by>', views.following_posts, name="following"),'''

'''path('/<username>', views.profile, name="profile"),'''
'''path('following/<str:username>', views.following, name="following"),'''

'''path('profile/<str:created_by>', views.user_profile_view, name='profile'),
REVERESE ERROR, TRYING TO FIX, SO WHEN CLICKING USER FROM A POST DIRECTS TO THAT USERS PROFILE
'''