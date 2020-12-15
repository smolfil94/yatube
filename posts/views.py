from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404

from .forms import CommentForm, PostForm
from .models import Post, Group, User, Follow


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {
        'page': page,
        'paginator': paginator
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
        'group': group,
        "page": page,
        'paginator': paginator
    })


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'new_post.html', {'form': form})
    form.instance.author = request.user
    form.save()
    return redirect('index')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    return render(request, 'profile.html', {
        'author': author,
        'page': page,
        'paginator': paginator,
        'following': following,
    })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    comments = post.comments.all()
    form = CommentForm()
    return render(request, 'post.html', {
        'author': post.author,
        'post': post,
        'comments': comments,
        'form': form,
    })


@login_required
def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect('post', username, post_id)
    post = Post.objects.get(pk=post_id, author__username = username)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
        )
    if not form.is_valid():
        return render(request, 'new_post.html', {'form': form, 'post': post})
    form.save()
    return redirect('post', username, post_id)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return redirect('post', username=username, post_id=post_id)
    post = Post.objects.get(author__username=username, id=post_id)
    form.instance.post = post
    form.instance.author = request.user
    form.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {
        'page': page,
        'paginator': paginator
        })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user and not Follow.objects.filter(
        user=request.user,
        author=author
    ).exists():
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(Follow, user=request.user,
                      author__username=username).delete()
    return redirect("profile", username=username)
