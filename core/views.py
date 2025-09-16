from django.shortcuts import render, get_object_or_404
from django.utils.safestring import mark_safe
from django.http import HttpResponse, Http404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import re
from pathlib import Path
from .models import Page, Post


def home(request):
	# Render the simple home page that extends base.html
	return render(request, 'home.html')


def page_detail(request, path: str):
	page = get_object_or_404(Page, path=path.strip('/'))
	return render(request, 'core/page_detail.html', {
		'title': page.title,
		'content_html': mark_safe(page.content_html),
	})


def post_list(request):
	posts = Post.objects.all()[:50]
	return render(request, 'core/post_list.html', {
		'posts': posts,
	})


def post_detail(request, slug: str):
	post = get_object_or_404(Post, slug=slug)
	return render(request, 'core/post_detail.html', {
		'post': post,
		'content_html': mark_safe(post.content_html),
	})

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
