#!/usr/bin/python
'''Plugin for new_simple_cms

Create and insert metapost figures.
Offering two methods, inline and external reference.

Syntax:

Either (inline)

[[ FIG ] [ metapost_code ]]

Where metapost_code contains one figure description in common metapost
language e. g.:
beginfig(n);
% code
endfig;

or (as reference to separate metapost file)

[[ FIG_EXT ] [ n, description ]]

Where n is the figure number in an external metapost file.
Only one external metapost file is allowed per directory.
It can contain multiple figures in above syntax.
Further this method offers an optional description.

For external figures to work PROCESS_MP has to be set to true in config (default).

The figures are wrapped in a default template. Special configuration settings 
e.g. the default template, resolution, size are defined in modules.metapost_handler.'''

# Imports
# python
import os

# global config variables
from config import *

# processing function
from modules.metapost_handler import process_metapost, MP_EXT, check_mp


# Settings
# file name for resulting inline images/files
BASE_FILE_NAME = 'fig-plugin-xxx555'

# img tag
IMG_TAG = '<img style="width:auto;" alt="{alt}" src="{img_src}" />\n'

# description tag (explicit)
DESC_TAG = '<p class="comment">Fig. {n}: {description}</p>\n'


# Functions
#

def metapost(subdir, plugin_in):
	'''Create figure from specified metapost code and insert a reference/link.
	
Using the processing function from modules.metapost_handler.'''
	
	outdir = os.path.join(CONTENT_DIR, subdir)
	
	# call the processing function
	process_metapost(outdir, BASE_FILE_NAME, plugin_in)
	
	# extract the figure number
	beginfig_mp = plugin_in.split(';')[0].strip()
	fig_num = beginfig_mp[-2]
	
	img_alt = "Figure / Illustration Nr."+fig_num
	
	# create tag
	img_tag = IMG_TAG.format(alt=img_alt, img_src=BASE_FILE_NAME+'-'+fig_num+'.png')
	
	# return
	return img_tag
	

def metapost_ext(subdir, plugin_in):
	'''Insert image tags/references.'''
	
	dir = os.path.join(CONTENT_DIR, subdir)
	
	# find the corresponding .mp file
	mp_file = check_mp(subdir)
	
	if not mp_file:
		return "Error: Plugin FIG_EXT: External metapost file not found."
	
	mp_filename = mp_file.split('.')[0]
	
	# split plugin content
	fig_num = plugin_in.split(',')[0].strip()
	
	fig_desc = plugin_in.split(',')[1].strip().strip('"').strip()
	
	# create name
	png_filename = mp_filename+'-'+fig_num+'.png'
	
	# create tag
	img_tag = IMG_TAG.format(alt=fig_desc, img_src=png_filename)
	desc_tag = DESC_TAG.format(n=fig_num, description=fig_desc)
	full_tag = img_tag+desc_tag
	
	# return
	return full_tag

