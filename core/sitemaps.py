from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Page, Post


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        # Add named URL patterns for static views if any
        return ['home']

    def location(self, item):
        return reverse(item)


class PageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Page.objects.filter(status='publish')

    def location(self, obj):
        # Pages are routed by path in core.urls -> page_detail
        if not obj.path:
            return '/'
        return f"/{obj.path.strip('/')}" if obj.path else '/'

    def lastmod(self, obj):
        return obj.modified_at or obj.published_at or obj.updated


class PostSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Post.objects.filter(status='publish')

    def location(self, obj):
        return f"/blog/{obj.slug}/"

    def lastmod(self, obj):
        return obj.modified_at or obj.published_at or obj.updated
