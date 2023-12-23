from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse

from django import forms

from .models import User, Post, UserProfile
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from django.core.paginator import Paginator

from django.http import JsonResponse

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
    posts = Post.objects.all().order_by('-created_date')
    paginator = Paginator(posts, 5)
    if request.GET.get("page") != None:
        try:
            posts = paginator.page(request.GET.get("page"))
        except:
            posts = paginator.page(1)
    else:
        posts = paginator.page(1)
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
        post.post = request.POST.get('post', '')  # 'post' is the name attribute of the textarea
        post.save()
        return HttpResponseRedirect(reverse("network:allposts"))
    else:
        return render(request, "network/edit_post.html", {"post": post})


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
        else:
            # Increment the like count and add the user to the likes
            post.likes.add(user)

        post_data = {
            'pk': post.id,
            'fields': {
                'likes': list(post.likes.values_list('id', flat=True)),
                'user_id': user.id
            }
        }

        return JsonResponse([post_data], safe=False)
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    
def user_profile_view(request, username):
    if(request.user.is_authenticated):
        user = get_object_or_404(User, username=username)
        user_profile = UserProfile.objects.get(user=user)
        posts = Post.objects.filter(created_by=user).order_by('-created_date')

        paginator = Paginator(posts, 2)
        if request.GET.get("page") != None:
            try:
                posts = paginator.page(request.GET.get("page"))
            except:
                posts = paginator.page(1)
        else:
            posts = paginator.page(1)



        current_profile = UserProfile.objects.get(user=request.user)
        followed = current_profile.following_users.filter(username=username).exists()
        print(followed)
        context = {
            'username':username,
            'user_profile': user_profile,
            'posts': posts,
            'followed': followed,
        }

        return render(request, 'network/profile.html', context)
    else:
        login_url = reverse('network:login')
        return redirect(login_url)


@login_required
def following_posts(request):
    # Get the current user's profile
    user_profile = UserProfile.objects.get(user=request.user)

    # Get the list of users that the current user follows
    following_users = user_profile.following_users.all()

    # Get the posts made by the users that the current user follows
    posts = Post.objects.filter(created_by__in=following_users).order_by("-created_date")

    paginator = Paginator(posts, 2)
    if request.GET.get("page") != None:
        try:
            posts = paginator.page(request.GET.get("page"))
        except:
            posts = paginator.page(1)
    else:
        posts = paginator.page(1)

    return render(request, 'network/following.html', {'posts': posts})


@login_required
def follow_profile(request):
    if request.method == 'POST':
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

        return redirect('network:profile', username=posted_by)

    return redirect('network:allposts')
