from django.contrib.auth.models import User
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ('-name',)


class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    excerpt = models.TextField(max_length=500)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='posts')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    admin_note = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'پیش نویس'),
            ('pending', 'در انتظار تایید'),
            ('published', 'منتشر شده'),
            ('rejected', 'رد شده'),
        ],
        default='pending'
    )
    def __str__(self):
        return f'{self.title} by {self.user.username}'

    class Meta:
        ordering = ('-created',)

    @property
    def likes_count(self):
        return self.reactions.filter(
            reaction='like'
        ).count()

    @property
    def dislikes_count(self):
        return self.reactions.filter(
            reaction='dislike'
        ).count()

class Comment(MPTTModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    like = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class PostReactions(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    CHOICES = (
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=10, choices=CHOICES)

    class Meta:
        unique_together = ('post', 'user')