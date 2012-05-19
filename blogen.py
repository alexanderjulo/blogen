#!/usr/bin/python2.7 

from flask import Flask
from flaskext.flatpages import FlatPages
from flaskext.script import Manager
from flask_frozen import Freezer

gen = Flask(__name__)
gen.config.from_pyfile('blogen.cfg')
pages = FlatPages(gen)
cli = Manager(gen)
static = Freezer(gen)

@gen.route('/')
def index():
	pass
	
@gen.route('/<page>/')
def page(page):
	return pages.get_or_404(page).html
		
@gen.route('/blog/')
def posts():
	pass
	
@gen.route('/blog/<post>/')
def post(post):
	pass
	
# cli-interface
@cli.command
def build():
	static.freeze()

if __name__ == '__main__':
	cli.run()
		
	