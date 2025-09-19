from django.shortcuts import render, get_object_or_404
from django.utils.safestring import mark_safe
from django.http import HttpResponse, Http404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import select_template
import re
from pathlib import Path
from .models import Page, Post, PublishStatus


def home(request):
	# Render the home page and, if available, apply SEO overrides from the Page with path='home'
	seo_ctx = {}
	try:
		page = Page.objects.get(path='home')
		from django.utils.html import strip_tags
		def _truncate(s, n=155):
			s = (s or '').strip()
			return (s[: n - 1] + '…') if len(s) > n else s
		seo_ctx = {
			'seo_title': page.seo_title or page.title,
			'seo_description': page.seo_description or _truncate(strip_tags(page.excerpt_html or '')),
			'seo_keywords': page.seo_keywords,
			'og_image_url': page.seo_image_url or None,
			# Expose a title the homepage template/partials can use for H1
			'page_title': page.title,
		}
	except Page.DoesNotExist:
		pass
	return render(request, 'home.html', seo_ctx)


def page_detail(request, path: str):
	page = get_object_or_404(Page, path=path.strip('/'))
	# Gate unpublished content: allow staff to preview drafts; 404 for others
	if page.status != PublishStatus.PUBLISH and not request.user.is_staff:
		raise Http404()
	# Prepare per-page SEO overrides
	seo_title = page.seo_title or page.title
	# Prefer explicit seo_description; else derive from excerpt_html (strip tags lightly)
	from django.utils.html import strip_tags
	derived_desc = strip_tags(page.excerpt_html).strip()
	# SERP-friendly truncation ~155 chars
	def _truncate(s, n=155):
		s = (s or '').strip()
		return (s[: n - 1] + '…') if len(s) > n else s
	seo_description = page.seo_description or _truncate(derived_desc)
	# Prefer a template based on path/slug if present; else fall back to generic
	candidates = [
		f"pages/{page.path}.html",
		f"pages/{page.slug}.html",
		"core/page_detail.html",
	]
	tpl = select_template(candidates)
	# OG type and last modified
	lastmod_dt = page.modified_at or page.published_at or page.updated
	lastmod_iso = lastmod_dt.isoformat() if lastmod_dt else None
	ctx = {
		'page': page,
		'title': page.title,
		'content_html': mark_safe(page.content_html),
		'seo_title': seo_title,
		'seo_description': seo_description,
		'seo_keywords': page.seo_keywords,
		'og_image_url': page.seo_image_url or None,
		'og_type': 'article',
		'lastmod_iso': lastmod_iso,
	}
	return HttpResponse(tpl.render(ctx, request))


def post_list(request):
	# Show only published posts to public; staff can see drafts in list
	qs = Post.objects.all()
	if not request.user.is_staff:
		qs = qs.filter(status=PublishStatus.PUBLISH)
	posts = qs[:50]
	return render(request, 'core/post_list.html', {
		'posts': posts,
	})


def post_detail(request, slug: str):
	post = get_object_or_404(Post, slug=slug)
	if post.status != PublishStatus.PUBLISH and not request.user.is_staff:
		raise Http404()
	from django.utils.html import strip_tags
	def _truncate(s, n=155):
		s = (s or '').strip()
		return (s[: n - 1] + '…') if len(s) > n else s
	derived_desc = strip_tags(post.excerpt_html or post.content_html).strip()
	seo_title = post.seo_title or post.title
	seo_description = post.seo_description or _truncate(derived_desc)
	candidates = [
		f"posts/{post.slug}.html",
		"core/post_detail.html",
	]
	tpl = select_template(candidates)
	# OG type and last modified
	lastmod_dt = post.modified_at or post.published_at or post.updated
	lastmod_iso = lastmod_dt.isoformat() if lastmod_dt else None
	ctx = {
		'post': post,
		'content_html': mark_safe(post.content_html),
		'seo_title': seo_title,
		'seo_description': seo_description,
		'seo_keywords': post.seo_keywords,
		'og_image_url': post.seo_image_url or None,
		'og_type': 'article',
		'lastmod_iso': lastmod_iso,
	}
	return HttpResponse(tpl.render(ctx, request))


def search(request):
	"""Simple site search across Page and Post titles and content_html."""
	from django.db.models import Q
	q = (request.GET.get('q') or '').strip()
	pages = posts = []
	if q:
		pages_qs = Page.objects.filter(
			Q(title__icontains=q) | Q(content_html__icontains=q)
		)
		posts_qs = Post.objects.filter(
			Q(title__icontains=q) | Q(content_html__icontains=q)
		)
		if not request.user.is_staff:
			pages_qs = pages_qs.filter(status=PublishStatus.PUBLISH)
			posts_qs = posts_qs.filter(status=PublishStatus.PUBLISH)
		pages = list(pages_qs[:20])
		posts = list(posts_qs[:20])
	ctx = {
		'q': q,
		'pages': pages,
		'posts': posts,
		'seo_title': f"Search results for '{q}'" if q else "Search",
		'seo_description': "Search pages and articles from L+C Psychological Services.",
		'og_type': 'website',
	}
	return render(request, 'core/search.html', ctx)

# Create your views here.


def import_preview(request):
	"""
	Serve the copied lcpsych.html as-is but rewrite WordPress upload URLs to
	local /media basenames so downloaded assets display. Intended for design
	parity comparison only.
	"""
	src_path = Path(settings.BASE_DIR) / 'lcpsych.html'
	if not src_path.exists():
		raise Http404('lcpsych.html not found at project root')
	html = src_path.read_text(encoding='utf-8')

	# Rewrite wp uploads to local media by basename
	def _rewrite_uploads(match: re.Match) -> str:
		full = match.group(0)
		url = match.group('url')
		# Extract basename
		basename = url.rstrip('/').split('/')[-1]
		if basename:
			return full.replace(url, f"/media/{basename}")
		return full

	pattern = re.compile(r"(?P<prefix>(?:src|href)=[\"'])(?P<url>https?://(?:www\.)?lcpsych\.com/wp-content/uploads/[^\"']+)(?P<suffix>[\"'])",
						 re.IGNORECASE)
	html = pattern.sub(lambda m: m.group('prefix') + f"/media/{m.group('url').rstrip('/').split('/')[-1]}" + m.group('suffix'), html)

	# Optional: normalize same-site anchor links to local anchors
	html = re.sub(r"href=\"https?://(?:www\.)?lcpsych\.com/(?:#([^\"']+))\"", r'href="#\1"', html, flags=re.IGNORECASE)

	return HttpResponse(html, content_type='text/html')


@csrf_exempt
def cloudflare_rum(request):
	"""No-op endpoint to absorb Cloudflare RUM POSTs without CSRF.

	Accepts POSTs at /cdn-cgi/rum and returns 204 No Content to avoid log noise.
	"""
	if request.method == 'POST':
		return HttpResponse(status=204)
	# For any other method, return 405 to indicate it's not supported
	return HttpResponse(status=405)


def cloudflare_email_decode_js(request):
	"""Serve a minimal stub for Cloudflare email decode script to avoid 404 noise.

	This script is often injected by copied markup; we don't need its behavior
	locally, so a harmless no-op is sufficient.
	"""
	js = (
		"/*! Cloudflare email-decode stub */\n"
		"// Intentionally left blank for local environment.\n"
	)
	resp = HttpResponse(js, content_type='application/javascript')
	# Cache briefly to reduce requests during dev
	resp['Cache-Control'] = 'public, max-age=300'
	return resp


@csrf_exempt
def wp_admin_ajax_stub(request):
	"""Local stub for WordPress admin-ajax.php to avoid external calls.

	Returns a minimal 204 for POST and empty JSON for GET.
	"""
	if request.method == 'POST':
		return HttpResponse(status=204)
	return HttpResponse('{"ok": true}', content_type='application/json')


@csrf_exempt
def wp_json_stub(request):
	"""Local stub for WordPress REST API endpoints used by copied scripts."""
	return HttpResponse('{"name": "Local WP JSON Stub"}', content_type='application/json')
