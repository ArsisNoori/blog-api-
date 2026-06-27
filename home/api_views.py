# posts/api_views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Post, Category, Comment, PostReactions
from .serializers import PostSerializer, CategorySerializer
from .serializers import CommentSerializer


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Post.objects.filter(
            status='published'
        ).select_related('category', 'user')

        q = self.request.query_params.get('q')
        if q:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q) |
                Q(user__username__icontains=q)
            )
        return queryset

    def perform_create(self, serializer):
        from slugify import slugify
        title = serializer.validated_data['title']
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while Post.objects.filter(slug=slug).exists():
            slug = f'{base_slug}_{counter}'
            counter += 1
        serializer.save(user=self.request.user, slug=slug)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return Post.objects.select_related('category', 'user')

    def get_object(self):
        obj = get_object_or_404(Post, slug=self.kwargs['slug'])
        # فقط owner یا admin می‌تونه ویرایش/حذف کنه
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.user != self.request.user and not self.request.user.is_superuser:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied()
        return obj


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [permissions.AllowAny]


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # فقط comment های root (بدون parent) برمی‌گردونیم
        # replies داخل خود comment هستن
        post_slug = self.kwargs['slug']
        return Comment.objects.filter(
            post__slug=post_slug,
            parent=None
        ).select_related('user')

    def perform_create(self, serializer):
        post = get_object_or_404(Post, slug=self.kwargs['slug'])
        serializer.save(user=self.request.user, post=post)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.select_related('user')

    def get_object(self):
        obj = get_object_or_404(Comment, pk=self.kwargs['pk'])
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.user != self.request.user and not self.request.user.is_superuser:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied()
        return obj


class PostReactionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        reaction_type = request.data.get('reaction')

        if reaction_type not in ['like', 'dislike']:
            return Response(
                {'error': 'reaction must be like or dislike'},
                status=status.HTTP_400_BAD_REQUEST
            )

        obj, created = PostReactions.objects.get_or_create(
            post=post,
            user=request.user,
            defaults={'reaction': reaction_type}
        )

        if not created:
            if obj.reaction == reaction_type:
                obj.delete()
                return Response({'status': 'removed'})
            else:
                obj.reaction = reaction_type
                obj.save()

        return Response({'status': 'ok', 'reaction': reaction_type})


class LikeCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)

        if request.user in comment.like.all():
            comment.like.remove(request.user)
            return Response({'status': 'unliked'})
        else:
            comment.like.add(request.user)
            return Response({'status': 'liked'})