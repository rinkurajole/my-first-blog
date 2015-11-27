from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post, Comment
from django.contrib.auth.models import User
from .forms import PostForm, CommentForm, UserForm
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required


def post_list(request):
	posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
	return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if request.user.is_superuser:
                post.published_date = timezone.now()
            post.save()
            return redirect('blog.views.post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

def user_login(request, *args, **kwargs):
    if request.user.is_authenticated():
        return redirect('blog.views.post_list')
    else:
        return login(request, *args, **kwargs)

def register(request):
    if request.user.is_authenticated():
        return redirect('blog.views.post_list')
    if request.method == "POST":
        user = UserForm(request.POST)
        if user.is_valid():
            user.save()
            newpass = request.POST['password']
            absuser = User.objects.get(username__exact = request.POST['username'])
            absuser.set_password(newpass)
            absuser.is_active = True
            absuser.save()
            return redirect('blog.views.user_login')
        else:
            html = render(request, 'registration/register.html', {'form': user})
            return HttpResponse(html)
    elif request.method == "GET":
        form = UserForm()
        return render(request, 'registration/register.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('blog.views.post_detail', pk=post.pk)
    else:
        return render(request, 'blog/post_edit.html', {'post': post})

@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('blog.views.post_detail', pk=pk)

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('blog.views.post_list')

@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            comment.approve()
            return redirect('blog.views.post_detail', pk=post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('blog.views.post_detail', pk=post_pk)
# Create your views here.
 