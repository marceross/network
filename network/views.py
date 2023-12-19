from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse

from django import forms

from .models import User, Post, UserProfile
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from django.core.serializers import serialize


class NewPost(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ["created_by", "created_date", "likes"]
        # Override the widget for the 'content' field
        widgets = {
            'post': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        }
        # Hide the label for the 'content' field
        labels = {
            'post': '',
    }


def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("network:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("network:index"))
    else:
        return render(request, "network/register.html")
    
is_following = False
def all_posts(request):

    try:
        posts = Post.objects.order_by("-created_date").all()

        if request.user.is_authenticated:
            user_profile = UserProfile.objects.get_or_create(user=request.user)[0]

            for post in posts:
                post.is_following = user_profile.following_users.filter(username=post.created_by.username).exists()

                    
        return render(request, 'network/allposts.html', {'posts': posts, 'user_profile': user_profile, 'is_following': is_following})

    except Exception as e:
        print(f"Exception in all_posts view: {e}")
        return render(request, 'network/allposts.html', {'posts': posts})


@login_required
def create_post(request):
    if request.method== "POST":
        form = NewPost(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.created_by = request.user
            post.save()
            return  HttpResponseRedirect(reverse("network:allposts"))
        else:
            return render(request, "network/create_post.html", {"form": form})
    return render(request, "network/create_post.html", {"form": NewPost()})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == "POST":
        edit = NewPost(request.POST, instance=post)
        if edit.is_valid():
            edited_post = edit.save(commit=False)
            edited_post.save()
            return HttpResponseRedirect(reverse("network:allposts"))
    else:
        edit = NewPost(instance=post)
        return render(request, "network/create_post.html", {"form": edit, "post": post})
    
@login_required
def following_posts(request):
    # Get the current user's profile
    user_profile = UserProfile.objects.get(user=request.user)

    # Get the list of users that the current user follows
    following_users = user_profile.following_users.all()

    # Get the posts made by the users that the current user follows
    posts = Post.objects.filter(created_by__in=following_users).order_by("-created_date")

    return render(request, 'network/following.html', {'posts': posts})



@require_POST
def like_post(request, post_id):
    user = request.user  
    if user.is_authenticated:
        post = get_object_or_404(Post, id=post_id)

        # Check if the user has already liked the post
        if user in post.likes.all():
            # User has already liked the post, handle this as needed
            post.likes.remove(user)
            return redirect('network:allposts')

        # Increment the like count and add the user to the likes
        post.likes.add(user)
        post.save()

        # Serialize the updated post data
        post_data = serialize('json', [post])
        return redirect('network:allposts')
    else:
        return redirect('network:allposts')




'''def profile(request, username):
    profile = UserProfile.objects.get(user=username)
    return render(request, 'network/profile.html', {'profile': profile})'''


'''class UserProfileView(LoginRequiredMixin, ListView):
    model = Post  # Using the Post model for the ListView, change this if needed
    template_name = 'profile.html'
    context_object_name = 'posts'
    ordering = ['-created_date']  # Display posts in reverse chronological order

    def get_queryset(self):
        # Get the user's own posts
        return Post.objects.filter(created_by=self.request.user)

    def get_context_data(self):
        context = super().get_context_data()
        # Get the user's profile
        user_profile = UserProfile.objects.get(user=self.request.user)
        context['user_profile'] = user_profile
        return context'''
    
def user_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    user_profile = UserProfile.objects.get(user=user)
    posts = Post.objects.filter(created_by=user).order_by('-created_date')
    
    context = {
        'user_profile': user_profile,
        'posts': posts,
    }

    return render(request, 'network/profile.html', context)



    

    
'''def following(request, username):

    following_profiles = UserProfile.objects.get(user=username).following.all()

    # Get posts from the users that the current user is following
    posts = Post.objects.filter(user__in=following_profiles).order_by('-timestamp')

    return render(request, 'network/following.html', {'posts': posts})
'''


'''https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-display/
Excellent, able to add pagination later
https://docs.djangoproject.com/en/5.0/topics/pagination/#paginating-a-list-view'''


'''@login_required
class FollowingPostsView(ListView):
    model = Post
    template_name = 'following.html'
    context_object_name = 'posts'

    def get_queryset(self):
        # Get the current user's profile
        user_profile = UserProfile.objects.get(user=self.request.user)

        # Get the posts of users that the current user follows
        following_users = user_profile.following_users.all()
        return Post.objects.filter(created_by__in=following_users).order_by('-created_date')'''
    

'''@login_required
def following_posts_view(request, username):
    # Get or create the current user's profile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Assuming you want to filter posts based on the specified username
    following_user = User.objects.get(username=username)
    following_users = user_profile.following_users.all()
    
    if following_user in following_users:
        posts = Post.objects.filter(created_by=following_user).order_by('-created_date')
    else:
        posts = []

    context = {'posts': posts, 'following_user': following_user}
    return render(request, 'following.html', context)'''


@login_required
def following_posts(request):
    # Get the current user's profile
    user_profile = UserProfile.objects.get(user=request.user)

    # Get the list of users that the current user follows
    following_users = user_profile.following_users.all()

    # Get the posts made by the users that the current user follows
    posts = Post.objects.filter(created_by__in=following_users).order_by("-created_date")

    return render(request, 'network/following.html', {'posts': posts})


def follow_toggle(request):
    posted_by = request.POST.get('posted_by')

    user_profile = get_object_or_404(UserProfile, user=request.user)
    to_follow_user, created = User.objects.get_or_create(username=posted_by)
    to_follow_profile, created = UserProfile.objects.get_or_create(user=to_follow_user)

    if user_profile.following_users.filter(username=posted_by).exists():
        user_profile.following_users.remove(to_follow_user)
        to_follow_profile.followers.remove(request.user)
    else:
        user_profile.following_users.add(to_follow_user)
        to_follow_profile.followers.add(request.user)

    return redirect('network:allposts')    