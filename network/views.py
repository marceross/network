from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from django import forms

from .models import User, Post, UserProfile
from django.contrib.auth.decorators import login_required


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


def all_posts(request):
    posts = Post.objects.order_by("-created_date").all()
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
    
@login_required
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



def follow(request):
    try:
        followed = True if (request.user.is_authenticated and
                UserProfile.followers.filter(pk=request.user.id).first()) else False

        if request.POST.get('add_follow'):
            if not followed:
                UserProfile.followers.add(request.user)
            else:
                UserProfile.followers.remove(request.user)
            followed = not followed
    
    except UserProfile.DoesNotExist:
        raise Http404("Listing not found.")


