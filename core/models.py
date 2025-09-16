from django.db import models
from django.utils.text import slugify


class Timestamped(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class Category(Timestamped):
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)
	description = models.TextField(blank=True)
	wp_id = models.IntegerField(null=True, blank=True, db_index=True)

	def __str__(self):
		return self.name


class Tag(Timestamped):
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)
	description = models.TextField(blank=True)
	wp_id = models.IntegerField(null=True, blank=True, db_index=True)

	def __str__(self):
		return self.name


class Page(Timestamped):
	title = models.CharField(max_length=500)
	slug = models.SlugField(max_length=255)
	path = models.CharField(max_length=1000, unique=True, help_text="Slash-separated path without leading/trailing slash")
	excerpt_html = models.TextField(blank=True)
	content_html = models.TextField()
	parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
	menu_order = models.IntegerField(default=0)
	status = models.CharField(max_length=50, default='publish')
	original_url = models.URLField(blank=True)
	published_at = models.DateTimeField(null=True, blank=True)
	modified_at = models.DateTimeField(null=True, blank=True)
	wp_id = models.IntegerField(db_index=True)
	wp_type = models.CharField(max_length=50, default='page')

	class Meta:
		unique_together = (('wp_id', 'wp_type'),)
		ordering = ['menu_order', 'title']

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.title)[:255]
		if self.path:
			self.path = self.path.strip('/')
		else:
			# derive from parent
			parts = []
			if self.parent and self.parent.path:
				parts.append(self.parent.path)
			parts.append(self.slug)
			self.path = '/'.join([p for p in parts if p])
		super().save(*args, **kwargs)


class Post(Timestamped):
	title = models.CharField(max_length=500)
	slug = models.SlugField(max_length=255, unique=True)
	excerpt_html = models.TextField(blank=True)
	content_html = models.TextField()
	status = models.CharField(max_length=50, default='publish')
	original_url = models.URLField(blank=True)
	published_at = models.DateTimeField(null=True, blank=True)
	modified_at = models.DateTimeField(null=True, blank=True)
	categories = models.ManyToManyField(Category, blank=True)
	tags = models.ManyToManyField(Tag, blank=True)
	wp_id = models.IntegerField(db_index=True)
	wp_type = models.CharField(max_length=50, default='post')

	class Meta:
		unique_together = (('wp_id', 'wp_type'),)
		ordering = ['-published_at']

	def __str__(self):
		return self.title


class NavItem(Timestamped):
	title = models.CharField(max_length=255)
	url = models.CharField(max_length=1000)
	order = models.IntegerField(default=0)
	parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
	is_external = models.BooleanField(default=False)

	class Meta:
		ordering = ['order', 'title']

	def __str__(self):
		return self.title

# Create your models here.
