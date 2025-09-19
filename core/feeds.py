from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from .models import Post, PublishStatus


class LatestPostsFeed(Feed):
    title = "L+C Psychological Services — Latest Posts"
    link = "/blog/"
    description = "Updates on new articles from L+C Psychological Services."

    def items(self):
        return Post.objects.filter(status=PublishStatus.PUBLISH).order_by('-published_at')[:20]

    def item_title(self, item: Post):  # type: ignore[name-defined]
        return item.seo_title or item.title

    def item_description(self, item: Post):  # type: ignore[name-defined]
        # Feeds prefer plain text or safe snippets; keep it short
        from django.utils.html import strip_tags
        text = strip_tags(item.excerpt_html or item.content_html)
        return truncatechars(text, 300)

    def item_link(self, item: Post):  # type: ignore[name-defined]
        return reverse('post_detail', kwargs={'slug': item.slug})
