#!/usr/bin/python2.7 
from flask import Flask, render_template
from flaskext.themes import ThemeManager, setup_themes, render_theme_template
from flaskext.flatpages import FlatPages
from flaskext.script import Manager
from flask_frozen import Freezer

# some default settings, that can be overwritten
THEME='default'
FLATPAGES_EXTENSION='.md'

gen = Flask(__name__)
gen.config.from_object(__name__)
gen.config.from_pyfile('blogen.cfg')
setup_themes(gen, app_identifier='blogen')
pages = FlatPages(gen)
cli = Manager(gen)
static = Freezer(gen)

@gen.route('/')
def index():
	pass
	
@gen.route('/<page>/')
def page(page):
	return render_theme_template(gen.config['THEME'], 'page.html', content=pages.get_or_404(page).html)
		
@gen.route('/blog/')
def posts():
	pass
	
@gen.route('/blog/<post>/')
def post(post):
	pass
	
# inject some standard vars into templates
@gen.context_processor
def inject_settings():
	return dict(title=gen.config['TITLE'])
	
# cli-interface
@cli.command
def build():
	static.freeze()

if __name__ == '__main__':
	cli.run()
		
	