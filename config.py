#!/usr/bin/python
#
# Config file for new_simple_cms.py.
#
# Defining global variables here.
#
# (This has to be imported into every submodule!)
#
##


### General:
#
## UTC Delta
#   (Only used for directory listing times atm.)
UTC_DELTA='+1'


### Content:
#
## Content directory:
#   (Containing markdown input files, directory structure, images etc..)
CONTENT_DIR='content'

## Default pandoc-style title block lines:
#   (First lines in .markdown files, starting with %.
#    Need to be defined here cause I've to read them out separately.
#    The first three should not be changed, however you can add more.
#    For subcontent use the option below.)
REGULAR_TB_LINES=['title', 'author', 'date']

### Table of content depth:
#    (The level of HTML headers to be included.)
TOC_DEPTH='5'

### Templates:
#
## Directory where templates are stored:
TEMPLATES_DIR='templates'

## The final template for all pages:
#   (Containing page layout, header, footer, menu's etc..)
MAJOR_TEMPLATE='templates/base.html'

## Default template for the menu:
#   (Used for the main-menu.)
# This option is deprecated, cause the main-menu is created
#  (quick and dirty) by pandoc and markdown now.
#MENU_TEMPLATE='templates/main-menu.html'
#
## A default template containing one menu line:
#   (Used for the main-menu.)
# This option is deprecated, cause the main-menu is created
#  (quick and dirty) by pandoc and markdown now.
#MENU_LINE_TEMPLATE='templates/menu-line.html'

## Default template containing one link line:
#   (Used for the section-menu.)
LINK_LINE_TEMPLATE='templates/link-line.html'

## The final directory listing page template:
#   (Maybe the base template could be used...)
LISTING_TEMPLATE='templates/listing.html'

## Directory listing table template:
# --> Deprecated, listing table is "hard coded" in listing.py (faster and better)
#LISTING_TABLE_TEMPLATE='templates/listing-table.html'

## Directory listing table entry template:
# --> Deprecated, listing table is "hard coded" in listing.py (faster and better)
#LISTING_TABLE_LINE_TEMPLATE='templates/listing-table-line.html'

## Default doctype strings for xhtml 1 strict and transitional
DOCTYPE_STRING_STRICT='<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
DOCTYPE_STRING_TRANSITIONAL='<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\n  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'


#### Menu's:
#
## Name to use for the CSS class for active pages:
#   (Used for the active link in the menu!)
ACTIVE_CLASS_NAME='Active'

### Main menu:
#
## Name to use for homepage (index.html):
HOME_NAME='Home'

## Here a custom order for the main menu can be defined:
#   (Only for the top level.)
#   Should contain all directories including home as defined above.
#   But might also be used to omit some directories. (Untested !)
#   Should be [] if not used.
CUSTOM_MENU_ORDER=['Home', 'Projects', 'About me', 'Uploads']

### Section menu:
#
## Hidden page names:
#   (Full or partial names of pages you don't want to appear in the section menu.)
HIDDEN_PAGE_NAMES=['impressum']


### Subcontent:
#
## Define the subcontent types:
#   (These names will be used when looking for a page subcontent.)
#    --> And in the templates ? <--
SUBCONTENT_TYPES=['post']

## Include more meta information in a title block, e.g. time.
## Define the subcontent types, that have a custom pandoc-style title block:
INCLUDE_CUSTOM_TB=['post']

## Custom pandoc-style title block lines, for subcontent:
#   (First lines in .markdown files, starting with %.) 
CUSTOM_TB_LINES=['title', 'author', 'date', 'time']


### Directory listing:
#
## Name to use for the CSS class for directories:
# (Used in the listing table.)
DIR_CLASS_NAME='Directory'
## Name to use for the CSS class for links and broken links:
# (Used in the listing table.)
LINK_CLASS_NAME='Link'
BROKENLINK_CLASS_NAME='BrokenLink'
## Default value:
# (Need a global variable here. Should be empty.)
LISTING_PARENT_DIR=''


### Plugins:
#
## Default placeholder for plugin processing:
#   (Using the fact here that pandoc passes through HTML !)
PLUGIN_PLACEHOLDER='<div id="placeholder"></div>'

# Extensions
#
# Math processing
# (Process Pandoc math using latex and dvipng. Create and insert png images.)
PROCESS_MATH = True

# Metapost processing (external)
# Needed for external figures using the metapost plugin.
# (Look for a metapost file in each directory and process it if found. Create images.)
PROCESS_MP = True

# Produce PDF files !
# Produce a PDF for every page using Pandoc.
PRODUCE_PDF = True

### Publish:
#
## Directory:
PUBLISH_DIR='public'
