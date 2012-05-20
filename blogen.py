#!/usr/bin/python2.7 
from flask import Flask, Blueprint, render_template, url_for
from flaskext.themes import ThemeManager, setup_themes, render_theme_template
from flaskext.flatpages import FlatPages, pygmented_markdown
from flaskext.script import Manager
from flask_frozen import Freezer
import os

# some default settings, that can be overwritten
THEME='default'
FLATPAGES_EXTENSION='.md'

gen = Flask(__name__)
gen.config.from_object(__name__)
gen.config.from_pyfile('blogen.cfg')
setup_themes(gen, app_identifier='blogen', theme_url_prefix='/theme')

# subclassing flatpages, to enable multiple page roots
class FlexFlatPages(FlatPages):
	def __init__(self, app, root):
		app.config.setdefault('FLATPAGES_ROOT', 'pages')
		app.config.setdefault('FLATPAGES_EXTENSION', '.html')
		app.config.setdefault('FLATPAGES_ENCODING', 'utf8')
		app.config.setdefault('FLATPAGES_HTML_RENDERER', pygmented_markdown)
		app.config.setdefault('FLATPAGES_AUTO_RELOAD', 'if debug')
		self.app = app
		self.root = root
		
		#: dict of filename: (page object, mtime when loaded) 
		self._file_cache = {}
		
		app.before_request(self._conditional_auto_reset)
		
	def root(self):
		return os.path.join(self.app.root_path, self.root)

# create two instances of flatpages, one for the pages and one for the posts.	
pages = FlexFlatPages(gen, 'pages')
posts = FlexFlatPages(gen, 'posts')

cli = Manager(gen)

static = Freezer(gen)

@gen.route('/')
def index():
	return "Bla"
	
@gen.route('/<page>/')
def page(page):
	return render_theme_template(gen.config['THEME'], 'page.html', page=pages.get_or_404(page))
		
@gen.route('/blog/')
def postindex():
	return render_theme_template(gen.config['THEME'], 'index.html', list=posts)
	
@gen.route('/blog/<post>/')
def post(post):
	return render_theme_template(gen.config['THEME'], 'post.html', post=posts.get_or_404(post))
	
	
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
		
	