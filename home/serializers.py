# posts/serializers.py

from rest_framework import serializers
from .models import Post, Category, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='user.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    dislikes_count = serializers.IntegerField(read_only=True)
    image = serializers.ImageField(required=False)


    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content',
            'category', 'category_name', 'author',
            'image', 'status', 'likes_count', 'dislikes_count',
            'created', 'updated'
        ]
        read_only_fields = ['slug', 'status', 'created', 'updated']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='user.username', read_only=True)
    likes_count = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author', 'content',
            'parent', 'likes_count', 'replies',
            'created', 'updated'
        ]
        read_only_fields = ['created', 'updated']

    def get_likes_count(self, obj):
        return obj.like.count()

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []