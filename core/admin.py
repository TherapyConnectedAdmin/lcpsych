from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.conf import settings
from .models import Page, Post, Category, Tag
class PageAdminForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = [
            # SEO first
            'seo_title', 'seo_description', 'seo_keywords', 'seo_image_url',
            # Core
            'title', 'slug', 'path', 'status',
        ]
        widgets = {
            'seo_description': forms.Textarea(attrs={'rows': 3}),
            'seo_keywords': forms.Textarea(attrs={'rows': 3}),
        }



@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm
    list_display = ("title", "path", "status", "published_at")
    search_fields = ("title", "path", "content_html", "seo_title", "seo_description", "seo_keywords")
    list_filter = ("status",)
    ordering = ("title",)
    fieldsets = (
        ("SEO", {
            'fields': ("seo_title", "seo_description", "seo_keywords", "seo_image_url", "excerpt_preview", "serp_preview")
        }),
        ("Page routing", {
            'fields': ("title", "slug", "path", "status")
        }),
        ("Publishing", {
            'fields': ("published_at", "modified_at")
        }),
        ("Import metadata", {
            'classes': ('collapse',),
            'fields': ()
        }),
    )
    readonly_fields = ("serp_preview", "published_at", "modified_at", "excerpt_preview")

    class Media:
        css = {
            'all': ('admin/overrides.css',)
        }

    def serp_preview(self, obj: Page | None):
        base = (getattr(settings, 'BASE_URL', '') or '').rstrip('/')
        url = f"{base}/{obj.path}" if obj and getattr(obj, 'path', None) else f"{base}/"
        title = (getattr(obj, 'seo_title', '') or getattr(obj, 'title', '') or '') if obj else ''
        desc = (getattr(obj, 'seo_description', '') or getattr(obj, 'excerpt_html', '') or '') if obj else ''
        # basic trim for preview purposes
        title = (title[:60] + '…') if len(title) > 60 else title
        # naive strip tags for preview only
        import re
        desc_txt = re.sub(r"<[^>]+>", "", desc or '').strip()
        desc_txt = (desc_txt[:157] + '…') if len(desc_txt) > 158 else desc_txt
        return format_html(
            '<div style="border:1px solid #ddd;padding:8px;border-radius:6px">\n'
            '<div style="color:#1a0dab;font-size:18px;line-height:1.2">{}</div>\n'
            '<div style="color:#006621;font-size:14px">{}</div>\n'
            '<div style="color:#545454;font-size:13px">{}</div>\n'
            '</div>',
            title, url, desc_txt
        )
    serp_preview.short_description = "SERP preview"

    # ModelForm above controls widgets explicitly

    def excerpt_preview(self, obj: Page | None):
        import re
        if not obj:
            return ''
        source = getattr(obj, 'excerpt_html', '') or getattr(obj, 'content_html', '') or ''
        txt = re.sub(r"<[^>]+>", "", source).strip()
        return (txt[:157] + '…') if len(txt) > 158 else txt
    excerpt_preview.short_description = "Derived description preview"

    def save_model(self, request, obj: Page, form, change):
        from django.utils import timezone
        # Auto derive excerpt if missing
        if not obj.excerpt_html and obj.content_html:
            from django.utils.html import strip_tags
            txt = strip_tags(obj.content_html).strip()
            obj.excerpt_html = txt[:300]
        # Auto-generate content_html if empty
        if not obj.content_html:
            # Prefer seo_description or excerpt to build a simple hero block
            desc = (obj.seo_description or obj.excerpt_html or "").strip()
            body = f"<section class=\"hero\"><h1>{obj.title}</h1>" + (f"<p>{desc}</p>" if desc else "") + "</section>"
            obj.content_html = body
        # Auto-set published/modified timestamps
        now = timezone.now()
        from .models import PublishStatus
        if not obj.published_at and getattr(obj, 'status', '') == PublishStatus.PUBLISH:
            obj.published_at = now
        obj.modified_at = now
        super().save_model(request, obj, form, change)
class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            # SEO first
            'seo_title', 'seo_description', 'seo_keywords', 'seo_image_url',
            # Core
            'title', 'slug', 'status', 'categories', 'tags',
        ]
        widgets = {
            'seo_description': forms.Textarea(attrs={'rows': 3}),
            'seo_keywords': forms.Textarea(attrs={'rows': 3}),
        }


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ("title", "published_at", "status")
    search_fields = ("title", "content_html", "seo_title", "seo_description", "seo_keywords")
    list_filter = ("status", "categories")
    fieldsets = (
        ("SEO", {
            'fields': ("seo_title", "seo_description", "seo_keywords", "seo_image_url", "excerpt_preview", "serp_preview")
        }),
        ("Post", {
            'fields': ("title", "slug", "status", "categories", "tags")
        }),
        ("Publishing", {
            'fields': ("published_at", "modified_at")
        }),
        ("Import metadata", {
            'classes': ('collapse',),
            'fields': ()
        }),
    )
    readonly_fields = ("serp_preview", "published_at", "modified_at", "excerpt_preview")

    class Media:
        css = {
            'all': ('admin/overrides.css',)
        }

    def serp_preview(self, obj: Post | None):
        base = (getattr(settings, 'BASE_URL', '') or '').rstrip('/')
        url = f"{base}/blog/{obj.slug}/" if obj and getattr(obj, 'slug', None) else base
        title = (getattr(obj, 'seo_title', '') or getattr(obj, 'title', '') or '') if obj else ''
        desc = (getattr(obj, 'seo_description', '') or getattr(obj, 'excerpt_html', '') or getattr(obj, 'content_html', '') or '') if obj else ''
        title = (title[:60] + '…') if len(title) > 60 else title
        import re
        desc_txt = re.sub(r"<[^>]+>", "", desc or '').strip()
        desc_txt = (desc_txt[:157] + '…') if len(desc_txt) > 158 else desc_txt
        return format_html(
            '<div style="border:1px solid #ddd;padding:8px;border-radius:6px">\n'
            '<div style="color:#1a0dab;font-size:18px;line-height:1.2">{}</div>\n'
            '<div style="color:#006621;font-size:14px">{}</div>\n'
            '<div style="color:#545454;font-size:13px">{}</div>\n'
            '</div>',
            title, url, desc_txt
        )
    serp_preview.short_description = "SERP preview"

    # ModelForm above controls widgets explicitly

    def excerpt_preview(self, obj: Post | None):
        import re
        if not obj:
            return ''
        source = getattr(obj, 'excerpt_html', '') or getattr(obj, 'content_html', '') or ''
        txt = re.sub(r"<[^>]+>", "", source).strip()
        return (txt[:157] + '…') if len(txt) > 158 else txt
    excerpt_preview.short_description = "Derived description preview"

    def save_model(self, request, obj: Post, form, change):
        from django.utils import timezone
        # Auto derive excerpt if missing
        if not obj.excerpt_html and obj.content_html:
            from django.utils.html import strip_tags
            txt = strip_tags(obj.content_html).strip()
            obj.excerpt_html = txt[:300]
        # Auto-generate content_html if empty
        if not obj.content_html:
            desc = (obj.seo_description or obj.excerpt_html or "").strip()
            body = f"<article class=\"post\"><h1>{obj.title}</h1>" + (f"<p>{desc}</p>" if desc else "") + "</article>"
            obj.content_html = body
        # Auto-set published/modified timestamps
        now = timezone.now()
        from .models import PublishStatus
        if not obj.published_at and getattr(obj, 'status', '') == PublishStatus.PUBLISH:
            obj.published_at = now
        obj.modified_at = now
        super().save_model(request, obj, form, change)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "wp_id")
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "wp_id")
    search_fields = ("name",)

# NavItem admin removed; header uses static template markup
