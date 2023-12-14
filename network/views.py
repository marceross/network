from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django import forms

from .models import User, Post
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