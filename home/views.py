from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from . models import Post, Category, Comment, PostReactions
from . forms import CommentForm, PostForm ,RejectPostForm
from django.utils import timezone
from datetime import timedelta
from slugify import slugify

# Create your views here.


class HomeView(generic.ListView):
    model = Post
    template_name = 'home/index.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        queryset = Post.objects.filter(
            status='published'
        ).select_related(
            'category',
            'user'
        )
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q)|
                Q(user__username__icontains=q)|
                Q(category__name__icontains=q)


            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['categories'] = Category.objects.all()
        return context


class DetailView(generic.DetailView):
    model = Post
    template_name = 'home/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['comments'] = (
            Comment.objects
            .filter(post=self.object)
            .select_related('user')
        )

        context['comment_form'] = CommentForm()
        return context


class CreateCommentView(LoginRequiredMixin, generic.CreateView):
    model = Comment
    form_class = CommentForm
    http_method_names = ['post']  # فقط پذیرش POST

    def dispatch(self, request, *args, **kwargs):
        # دریافت پست و parent در ابتدا
        self.post_obj = get_object_or_404(Post, slug=kwargs['slug'])
        self.parent_comment = None

        parent_id = request.POST.get('parent_id') or request.GET.get('parent_id')
        if parent_id:
            self.parent_comment = get_object_or_404(Comment, id=parent_id, post=self.post_obj)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.user = self.request.user
        comment.post = self.post_obj
        comment.parent = self.parent_comment
        comment.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('home:post_detail', kwargs={'slug': self.post_obj.slug})


class UpdateCommentView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'home/update_comment.html'
    context_object_name = 'comment'

    def test_func(self):
        comment = self.get_object()
        return (
                self.request.user == comment.user and timezone.now() - comment.created < timedelta(minutes=5))

    def get_success_url(self):
        return reverse('home:post_detail',kwargs={'slug': self.object.post.slug})


class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, View):
    model = Comment
    template_name = 'home/comment_confirm_delete.html'
    context_object_name = 'comment'

    def test_func(self):
        comment = self.get_object()
        return(
                self.request.user == comment.user
                or self.request.user.is_superuser
                )

    def get_success_url(self):
        return reverse('home:post_detail',kwargs={'slug': self.object.post.slug})


class LikeCommentView(LoginRequiredMixin, View):

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)

        if request.user in comment.like.all():
            comment.like.remove(request.user)
        else:
            comment.like.add(request.user)

        return redirect(
            'home:post_detail',
            slug=comment.post.slug
        )


class CreatePostView(LoginRequiredMixin, generic.CreateView):
    model = Post
    template_name = 'home/post_form.html'
    form_class = PostForm

    def form_valid(self, form):
        post = form.save(commit=False)
        post.user = self.request.user
        post.is_published = False
        base_slug = slugify(post.title)
        slug = base_slug
        counter = 1
        while Post.objects.filter(slug=slug).exists():
            slug = f'{base_slug}_{counter}'
            counter += 1
        post.slug = slug
        post.save()
        messages.success(self.request, 'Post created successfully', 'success')
        self.object = post
        return super().form_valid(form)
    def get_success_url(self):
        return reverse(
            'home:post_submitted',
            kwargs={'slug': self.object.slug}
        )


class PostSubmittedView(LoginRequiredMixin,UserPassesTestMixin,generic.DetailView):
    model = Post
    template_name = 'home/post_submitted.html'
    context_object_name = 'post'
    slug_field = 'slug'

    def test_func(self):
        post = self.get_object()
        return (
            self.request.user == post.user
            or self.request.user.is_superuser
        )


class UpdatePostView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'home/post_form.html'
    def test_func(self):
        post = self.get_object()
        return (
                self.request.user == post.user or self.request.user.is_superuser
        )
    def get_success_url(self):
        return reverse('home:post_detail',kwargs={'slug': self.object.slug})


class DeletePostView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Post
    template_name = 'home/post_confirm_delete.html'
    slug_url_kwarg = 'slug'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.user or self.request.user.is_superuser

    def get_success_url(self):
        return reverse('home:home')


class PostReactionView(LoginRequiredMixin, View):
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        reaction_type = request.POST.get('reaction')
        obj,created = PostReactions.objects.get_or_create(
            post=post,
            user = request.user,
            defaults={
                'reaction': reaction_type
            }
        )
        if not created:
            if obj.reaction == reaction_type:
                obj.delete()
            else:
                obj.reaction = reaction_type
                obj.save()
        return redirect('home:post_detail', slug=post.slug)


class ManagePostsView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = Post
    template_name = 'home/admin_post_list.html'
    context_object_name = 'posts'
    paginate_by = 5

    def test_func(self):
        return self.request.user.is_superuser


class PublishPostView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        post.status = 'published'
        post.admin_note = ''
        post.save()

        return redirect('home:manage_posts')


class RejectPostView(LoginRequiredMixin,UserPassesTestMixin,generic.FormView):
    form_class = RejectPostForm
    template_name = 'home/reject_post.html'

    def test_func(self):
        return self.request.user.is_superuser

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(
            Post,
            slug=kwargs['slug']
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.post_obj.status = 'rejected'
        self.post_obj.admin_note = form.cleaned_data['admin_note']
        self.post_obj.save()

        return redirect('home:manage_posts')


class ReviewPostView(LoginRequiredMixin,UserPassesTestMixin,generic.DetailView):
    model = Post
    template_name = 'home/review_post.html'
    context_object_name = 'post'
    slug_field = 'slug'

    def test_func(self):
        return self.request.user.is_superuser


class AuthorDashboardView(LoginRequiredMixin, generic.ListView):
    model = Post
    template_name = 'home/author_dashboard.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(
            user=self.request.user
        ).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        posts = Post.objects.filter(
            user=self.request.user
        )

        context['total_posts'] = posts.count()
        context['published_posts'] = posts.filter(
            status='published'
        ).count()

        context['pending_posts'] = posts.filter(
            status='pending'
        ).count()

        context['rejected_posts'] = posts.filter(
            status='rejected'
        ).count()

        return context




















