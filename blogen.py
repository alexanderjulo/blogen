#!/usr/bin/python2.7
# ALL the imports!!1 
from __future__ import with_statement

import os
import itertools
import warnings

import yaml
import markdown
import werkzeug

from math import ceil
from string import replace, lower
from dateutil.parser import parse as timeparse
from datetime import datetime

from flask import Flask, render_template, url_for, redirect, abort
from flaskext.themes import ThemeManager, setup_themes, render_theme_template
from flaskext.script import Manager
from flask_frozen import Freezer



# some default settings, that can be overwritten
AUTHOR='anonymous'
THEME='default'
PER_PAGE=5
POSTSLUG='blog/%title%'
PAGESLUG='%title%'
DATETIME='%d. %B %Y'



# setup all the modules we need
gen = Flask(__name__)
gen.config.from_object(__name__)
gen.config.from_pyfile('blogen.cfg')
setup_themes(gen, app_identifier='blogen', theme_url_prefix='/theme')
cli = Manager(gen)
static = Freezer(gen)



# Here is some code I had to include to make things work
# unfortunately subclassing flask-flatpages was not enough,
# so I copied and adjusted it. the original source is:
# https://github.com/SimonSapin/Flask-FlatPages
def pygmented_markdown(text):
		try:
				import pygments
		except ImportError:
				extensions = []
		else:
				extensions = ['codehilite']
		return markdown.markdown(text, extensions)


def pygments_style_defs(style='default'):
		import pygments.formatters
		formater = pygments.formatters.HtmlFormatter(style=style)
		return formater.get_style_defs('.codehilite')
		
	
		
class Page(object):
	def __init__(self, path, full_path, meta_yaml, body, slug):
		self.path = path
		self.full_path = full_path
		self.body = body
		self._meta_yaml = meta_yaml
		self.html_renderer = pygmented_markdown
		self._slug = slug
		
	def __repr__(self):
		return '<Page %r>' % self.path
	
	@werkzeug.cached_property
	def html(self):
		return self.html_renderer(self.body)
	
	def __html__(self):
		return self.html
	
	@werkzeug.cached_property
	def meta(self):
		meta = yaml.safe_load(self._meta_yaml)
		if not meta:
			return {}
		assert isinstance(meta, dict)
		try:
			self.date = timeparse(meta['date'])
		except KeyError:
			self.date = datetime.fromtimestamp(os.path.getmtime(self.full_path))
		meta['date'] = self.date.strftime(gen.config['DATETIME'])
		try:
			meta['slug']
		except KeyError:
			rules = [
				('%title%', meta['title']),
				("%path%", self.path),
				("%year%", str(self.date.year)),
				("%month%", str(self.date.month)),
				("%day%", str(self.date.day)),
				("%hour%", str(self.date.hour)),
				("%minute%", str(self.date.minute)),
				(" ", "-")
			]
			slug = self._slug
			for (expression, replacement) in rules:
				slug = replace(slug, expression, replacement)
			meta['slug'] = lower(slug)
		try:
			meta['author']
		except KeyError:
			meta['author'] = gen.config['AUTHOR']
			
		return meta
		
	def __getitem__(self, name):
		return self.meta[name]
		

class FlatPages(object):
	def __init__(self, app, root, slug):
		self.app = app
		self.root = unicode(root)
		self._slug = slug

		#: dict of filename: (page object, mtime when loaded) 
		self._file_cache = {}

	def root(self):
		return os.path.join(self.app.root_path, self.root)
		
	def __iter__(self):
		"""Iterate on all :class:`Page` objects."""
		return self._pages.itervalues()
		
	def get(self, slug):
		pages = self._pages
		try:
			return pages[slug]
		except KeyError:
			return None
			
	def get_or_404(self, slug):
		page = self.get(slug)
		if not page:
			abort(404)
		return page
	
	@werkzeug.cached_property	
	def _pages(self):
		def _walk(directory, path_prefix=()):
			for name in os.listdir(directory):
				full_name = os.path.join(directory, name)
				if os.path.isdir(full_name):
					_walk(full_name, path_prefix + (name,))
				elif name.endswith('.md'):
					name_without_extension = name[:-len('.md')]
					path = u'/'.join(path_prefix + (name_without_extension,))
					page = self._load_file(path, full_name, self._slug)
					pages[page.meta['slug']] = page
		
		pages = {}
		_walk(self.root)
		return pages
	
	def _load_file(self, path, filename, slug):
		with open(filename) as fd:
			content = fd.read().decode('utf8')
		page = self._parse(content, path, filename, slug)
		return page
		
	def _parse(self, string, path, filename, slug):
		lines = iter(string.split(u'\n'))
		meta = u'\n'.join(itertools.takewhile(unicode.strip, lines))
		content = u'\n'.join(lines)
		return Page(path, filename, meta, content, slug)



# I stole this from http://flask.pocoo.org/snippets/44/
# well you can not really say stolen, as I adapted a lot of things
class Pagination(object):
		def __init__(self, source, page, per_page, objects):
				self.source = source
				self.page = page
				self.per_page = per_page
				
				# sort posts by date
				def getpagedate(page):
					date = ""
					if isinstance(page, Page):
						date = page.date
					else:
						date = source.get(page).date
					return date
				
				# if there is a list of posts given, sort the list
				# otherwise get all posts from the source and sort them
				if not objects:
					elements = source._pages
				else:
					elements = objects
				self.objects = sorted(elements, key=getpagedate, reverse=True)
				self.total_count = len(self.objects)
				
				# build content of current page
				if per_page == 0:
					current_strings = self.objects
				else:
					current_strings = self.objects[(page - 1)*per_page:(page)*per_page]
				current_objects = list()
				for element in current_strings:
					if isinstance(element, Page):
						current_objects.append(element)
					else:
						current_objects.append(source.get(element))
				self.current = current_objects
					

		@property
		def pages(self):
				if self.per_page == 0:
						return 1
				else:
					return int(ceil(self.total_count / float(self.per_page)))

		@property
		def has_prev(self):
				return self.page > 1

		@property
		def has_next(self):
				return self.page < self.pages

		def iter_pages(self, left_edge=2, left_current=2,
									 right_current=5, right_edge=2):
				last = 0
				for num in xrange(1, self.pages + 1):
						if num <= left_edge or (num > self.page - left_current - 1 and num < self.page + right_current) or num > self.pages - right_edge:
								if last + 1 != num:
										yield None
								yield num
								last = num

# a helper function to get the wanted page
def paginate(source, page, per_page=gen.config['PER_PAGE'], objects=None):
	return Pagination(source, page, per_page, objects)
		
		
						
# create two instances of flatpages, one for the pages and one for the posts.	
pages = FlatPages(gen, 'pages', PAGESLUG)
posts = FlatPages(gen, 'posts', POSTSLUG)



# This is what will be frozen later on
@gen.route('/', defaults={'page': 1})
@gen.route('/page/<int:page>/')
def postindex(page):
	return render_theme_template(gen.config['THEME'], 'index.html', pagination=paginate(posts, page=page))

@gen.route('/<path:url>/')
def decider(url):
	poss_page = pages.get(url)
	poss_post = posts.get(url)
	if poss_page and poss_post:
		print "error: duplicate url %s, at page %s and post %s" % (url, poss_page.path, poss_post.path)
		exit()
	elif poss_page:
		return page(url)
	elif poss_post:
		return post(url)
	else:
		return abort(404)
		

@gen.route('/<path:page>/')
def page(page):
	page = pages.get(page)
	return render_theme_template(gen.config['THEME'], 'page.html', page=page)
	
@gen.route('/<path:post>/')
def post(post):
	post = posts.get(post)
	return render_theme_template(gen.config['THEME'], 'post.html', element=post)

@gen.route('/tags/')
def tagindex():
	tags = []
	for post in posts:
		try:
			for tag in post.meta['tags']:
				if tag not in tags:
					tags.append(tag)
		except KeyError:
			pass
	return render_theme_template(gen.config['THEME'], 'tags.html', tags=sorted(tags))

@gen.route('/tag/<tag>/', defaults={'page': 1})
@gen.route('/tag/<tag>/page/<page>/')
def tag(tag, page):
	tagged = list()
	for post in posts:
			try:
				if tag in post.meta['tags']:
					tagged.append(post)
			except KeyError:
				pass
	return render_theme_template(gen.config['THEME'], 'index.html', pagination=paginate(posts, page=page, objects=tagged))

@gen.route('/archive/')
def archive():
	return render_theme_template(gen.config['THEME'], 'archive.html', pagination=paginate(posts, page=1, per_page=0))
	
# inject some standard vars into templates
@gen.context_processor
def inject_settings():
	return gen.config
	
@gen.context_processor
def inject_menu():
	menu = list()
	menu.append(('Blog', '/'))
	for page in pages:
		menu.append((page.meta['title'], url_for("page", page=page.meta['slug'])))
	try:
		menu = menu + gen.config['MENU']
	except KeyError:
		pass
	return dict(menu=menu)


# make sure all urls are found
@static.register_generator
def page_url_generator():
	for page in pages:
		yield 'page', {'page': page.meta['slug']}

@static.register_generator
def post_url_generator():
	for post in posts:
		yield 'post', {'post': post.meta['slug']}

@static.register_generator
def postindex_url_generator():
	pagination=paginate(posts, page=1)
	i = 1
	while i <= pagination.pages:
		yield 'postindex', {'page': i}
		i = i+1


# cli-interface
@cli.command
def setup():
	print "Setting necessary folders up."
	folders = ['pages', 'posts', 'static']
	for folder in folders:
		os.mkdir(folder)
	print "Setup finished."

@cli.command
def build():
	print "building static website.."
	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		static.freeze()
	print "finished!"

if __name__ == '__main__':
	cli.run()
		
	