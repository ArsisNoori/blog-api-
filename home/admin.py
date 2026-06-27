from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category__name', 'status', 'created', 'updated']
    list_filter = ['user', 'title', 'category__name', 'status']
    search_fields = ['title', 'content']
    raw_id_fields = ['user', 'category']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created', 'updated']