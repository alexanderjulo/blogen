# Blogen

## About
Blogen is a static site/blog generator. Everything it can do, is generate a range of pages and blog posts out of text files marked up in markdown.

It is based on [Flask](http://flask.pocoo.org/) and [Frozen-Flask](http://packages.python.org/Frozen-Flask/). It makes also use of [Flask-FlatPages](http://packages.python.org/Flask-FlatPages/) [Flask-Themes](http://packages.python.org/Flask-Themes) and [Flask-Script](http://packages.python.org/Flask-Script/).

It was inspired by [Nicolas's blog post](https://nicolas.perriault.net/code/2012/dead-easy-yet-powerful-static-website-generator-with-flask/) and was written and is maintained by [Alexander Jung-Loddenkemper](http://www.julo.ch/about).

## Setup
Download blogen as a [zip](https://github.com/alexex/blogen/zipball/master) and unzip it or clone the git repository:

``` bash
git clone git://github.com/alexex/blogen.git
```

Then do the following:

``` bash
cd blogen
python blogen.py setup
```

That's it already.

## Configuration
You should create a file `blogen.cnf` in the app's root. So far there are only two settings available, of which none is necessary but one recommended:

``` python
TITLE = "Your site's title." # this is recommended
THEME = "<ID>" # this defaults to the default bootstrap theme.
PER_PAGE = <NUM> # optional, the default is 5
SLUG = '<SLUG>' # optional, customize the slug to your likings, so far only %T, which is title is possible
DISQUS='<SHORTNAME>' # optional, disqus support, just enter your disqus shortname here
ANALYTICS='<ID>' # optional, analytics support, just enter your analytics ID here
SOCIAL=[('<Name>', '<URL>')] # optional, will create a social dropdown if given. put a number of tuples you like
MENU=[('<Name>', '<URL>')]  # optional, add custom entries to the menu.
```

## Blogging
Create files that end with `.md` in `pages` if you want pages and `posts` in posts. The part before the `.md` will also be the url of you page/post for now. Configuration is done via YAML. Create at least a `title`-tag in the beginning of the file. There will be more supported tags in the future.

## Building
Just run:

``` bash
python blogen.py build
```

## Deployment
I personally push my blog via git and have a deploy hook that executes blogen.py, but you can of course deploy how ever you want. Rsync might be a nice idea, for example.

## Templating
Blogen makes us of jinja2, just copy the `default`-theme from themes/ and adapt/rewrite it to your needs. Set `THEME` in your blogen.cnf to the id of your theme.
