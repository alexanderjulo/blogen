#!/usr/bin/python2.7
# ALL the imports!!1 
from flask import Flask, render_template, url_for, redirect
from flaskext.themes import ThemeManager, setup_themes, render_theme_template
from flaskext.flatpages import FlatPages, pygmented_markdown, Page
from flaskext.script import Manager
from flask_frozen import Freezer
import os
from math import ceil	



# some default settings, that can be overwritten
THEME='default'
FLATPAGES_EXTENSION='.md'
PER_PAGE=5



# setup all the modules we need
gen = Flask(__name__)
gen.config.from_object(__name__)
gen.config.from_pyfile('blogen.cfg')
setup_themes(gen, app_identifier='blogen', theme_url_prefix='/theme')
cli = Manager(gen)
static = Freezer(gen)



# Here is some code I hat to include to make things work
# subclassing flatpages, to enable multiple page roots
class FlexFlatPages(FlatPages):
	def __init__(self, app, root):
		app.config.setdefault('FLATPAGES_ROOT', 'pages')
		app.config.setdefault('FLATPAGES_EXTENSION', '.html')
		app.config.setdefault('FLATPAGES_ENCODING', 'utf8')
		app.config.setdefault('FLATPAGES_HTML_RENDERER', pygmented_markdown)
		app.config.setdefault('FLATPAGES_AUTO_RELOAD', 'if debug')
		self.app = app
		self.root = unicode(root)

		#: dict of filename: (page object, mtime when loaded) 
		self._file_cache = {}

		app.before_request(self._conditional_auto_reset)

	def root(self):
		return os.path.join(self.app.root_path, self.root)


# I stole this from http://flask.pocoo.org/snippets/44/
# well you can not really say stolen, as I adapted a lot of things
class Pagination(object):
		def __init__(self, source, page, per_page, objects):
				self.source = source
				self.page = page
				self.per_page = per_page
				
				# sort posts by date
				def getpagedate(page):
					if isinstance(page, str):
						return source.get(page).meta['date']
					if isinstance(page, Page):
						return page.meta['date']
				
				# if there is a list of posts given, sort the list
				# otherwise get all posts from the source and sort them
				if not objects:
					elements = source._pages
				else:
					elements = objects
				self.objects = sorted(elements, key=getpagedate, reverse=True)
				print self.objects
				self.total_count = len(self.objects)
				
				# build content of current page
				current_strings = self.objects[(page - 1)*per_page:(page)*per_page]
				current_objects = list()
				for element in current_strings:
					if isinstance(element, Page):
						current_objects.append(element)
					else:
						current_objects.append(source.get(element))
				self.current = current_objects
				print self.current
					

		@property
		def pages(self):
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
def paginate(source, page, objects=None):
	return Pagination(source, page, gen.config['PER_PAGE'], objects)
		

						
# create two instances of flatpages, one for the pages and one for the posts.	
pages = FlexFlatPages(gen, 'pages')
posts = FlexFlatPages(gen, 'posts')



# This is what will be frozen later on
@gen.route('/')
def index():
	homepage = pages.get('index')
	if homepage:
		return render_theme_template(gen.config['THEME'], 'page.html', homepage)
	else:
		return redirect(url_for('postindex'))
	
@gen.route('/<page>/')
def page(page):
	return render_theme_template(gen.config['THEME'], 'page.html', page=pages.get_or_404(page))

@gen.route('/blog/', defaults={'page': 1})
@gen.route('/blog/page/<int:page>/')
def postindex(page):
	return render_theme_template(gen.config['THEME'], 'index.html', pagination=paginate(posts, page=page))
	
@gen.route('/blog/<post>/')
def post(post):
	return render_theme_template(gen.config['THEME'], 'post.html', post=posts.get_or_404(post))

@gen.route('/blog/tags/')
def tagindex():
	tags = []
	for post in posts:
		for tag in post.meta['tags']:
			if tag not in tags:
				tags.append(tag)
	return render_theme_template(gen.config['THEME'], 'tags.html', tags=sorted(tags))

@gen.route('/blog/tag/<tag>/', defaults={'page': 1})
@gen.route('/blog/tag/<tag>/page/<page>/')
def tag(tag, page):
	tagged = list()
	for post in posts:
		if tag in post.meta['tags']:
			print str(post) + "has the tag" + tag
			tagged.append(post)
	return render_theme_template(gen.config['THEME'], 'index.html', pagination=paginate(posts, page=page, objects=tagged))
	
# inject some standard vars into templates
@gen.context_processor
def inject_settings():
	return gen.config
	
@gen.context_processor
def inject_menu():
	menu = list()
	menu.append(('Blog', '/blog/'))
	for page in pages:
		menu.append((page.meta['title'], url_for("page", page=page.path)))
	return dict(menu=menu)


# make sure all urls are found
@static.register_generator
def page():
	for page in pages:
		yield {'page': page.path}

@static.register_generator
def post():
	for post in posts:
		yield {'post': post.path}


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
	static.freeze()
	print "finished!"

if __name__ == '__main__':
	cli.run()
		
	