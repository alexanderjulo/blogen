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
You should create a file `blogen.cfg` in the app's root. So far there are only two settings available, of which none is necessary but one recommended:

``` python
TITLE = "Your site's title." # this is recommended
THEME = "<ID>" # this defaults to the default bootstrap theme.
PER_PAGE = <NUM> # optional, the default is 5
PAGESLUG = '<SLUG>' # optional, customize the slug for pages to your likings, see the Slugs section for more info on available parameters
POSTSLUG = '<SLUG>' # optional, customize the slug for posts to your likings, see the Slugs section for more info on available parameters
DISQUS='<SHORTNAME>' # optional, disqus support, just enter your disqus shortname here
ANALYTICS='<ID>' # optional, analytics support, just enter your analytics ID here
SOCIAL=[('<Name>', '<URL>')] # optional, will create a social dropdown if given. put a number of tuples you like
MENU=[('<Name>', '<URL>')]  # optional, add custom entries to the menu.
DATETIME='<FORMATSTRING>' # optional, how dates should be looking like on your blog, check out http://docs.python.org/library/datetime.html#strftime-strptime-behavior for further information
```

<h3 id="slugconfiguration">Slugs</h3>
The following parameters are available for configuration, you can combine them, however you like:

	%title% - title of your post/page
	%path% - path of the file
	%year% - year of the post
	%month% - month of the post
	%day% - day of the post
	%hour% - hour of the post
	%minute% - minute of the post 

For all time dependent vars applies the fact, that of no date is given the file modification date is used.

## Blogging
Create files that end with `.md` in `pages` if you want pages and `posts` in posts. The part before the `.md` will also be the url of you page/post for now. Configuration is done via YAML. Create at least a `title`-tag in the beginning of the file. For now title, date, tags and slug are supported. There will be more supported tags in the future.

A minimal example would look like this:

	title: Title of the post or page
	
	text
	
A more advanced example would like this:

	title: Title of the post or page
	date: 2012-06-18 18:30
	tags: [we, are, tags, "many tags"]
	slug: "i/am/a/custom-url"

## Building
Just run:

``` bash
python blogen.py build
```

## Deployment
I personally push my blog via git and have a deploy hook that executes blogen.py, but you can of course deploy how ever you want. Rsync might be a nice idea, for example.

## Templating
Blogen makes us of jinja2, just copy the `default`-theme from themes/ and adapt/rewrite it to your needs. Set `THEME` in your blogen.cnf to the id of your theme.
