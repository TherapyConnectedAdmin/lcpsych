from django.contrib import admin
from .models import Page, Post, Category, Tag, NavItem


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "path", "status", "published_at", "wp_id")
    search_fields = ("title", "path", "content_html")
    list_filter = ("status",)
    ordering = ("menu_order", "title")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "published_at", "status", "wp_id")
    search_fields = ("title", "content_html")
    list_filter = ("status", "categories")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "wp_id")
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "wp_id")
    search_fields = ("name",)

@admin.register(NavItem)
class NavItemAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "order", "parent")
    list_editable = ("order",)
    search_fields = ("title", "url")
