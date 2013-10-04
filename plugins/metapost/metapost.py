'''plugin for new_simple_cms

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

or (reference to separate metapost file)

[[ FIG_EXT ] [ filename, n, description ]]

Where n is the figure number in the external metapost file filename.
The file is expected in the current subdirectory and can contain multiple 
figures in the above syntax.
Further this method offers an optional description.
External figures are inserted as figures, using Pandoc figure syntax.

The figures are wrapped in a default metapost template. Special configuration 
settings e.g. the default template, resolution, size are defined in support_handler.
'''
# This file is part of new_simple_cms
#--------------------------------------------------------------------------------
#
# Copyright 2013 Cem Aydin
#
#--------------------------------------------------------------------------------
# See new_simple_cms.py for more information.

# Imports
# python
import os

# global config variables
import config

# processing function
from plugins.metapost.metapost_processing import process_metapost


# Settings
# file name for resulting inline images/files
BASE_FILE_NAME = 'fig-plugin-xxx555'

# img tag
# (inline)
IMG_TAG = '<img style="width:auto;" alt="{alt}" src="{src}" />'
# (external)
IMG_TAG_FIG = '<div class="figure"><img style="width:auto;" alt="{alt}" src="{src}" /></div>\n'

# description tag (explicit)
DESC_TAG = '<p class="comment">Fig. {n}: {desc}</p>\n'


# Functions
#

def metapost(subdir, plugin_in):
	'''Create figure from specified metapost code and insert a reference/link.
	
Using the processing function from modules.metapost_handler.'''
	
	# call the processing function
	process_metapost(subdir, BASE_FILE_NAME, plugin_in)
	
	# extract the figure number
	beginfig_mp = plugin_in.split(';')[0].strip()
	fig_num = beginfig_mp[-2]
	
	img_alt = "Figure "+fig_num
	img_src = BASE_FILE_NAME+'-'+fig_num+'.png'
	
	# create tag
	img_tag = IMG_TAG.format(alt=img_alt, src=img_src)
	
	# PDF production
	if config.PRODUCE_PDF:
		eps_filename = BASE_FILE_NAME+'-'+fig_num+'.eps'
		
		img_tag_md = "!["+img_alt+"]("+eps_filename+")"
		
	else:
		img_tag_md = ""
	
	# return
	return img_tag, img_tag_md
	

def metapost_ext(subdir, plugin_in):
	'''Insert image tags/references.'''
	
	dir = os.path.join(config.CONTENT_DIR, subdir)
	
	# split plugin content
	fig_fields = plugin_in.split(',')
	
	fig_filename = fig_fields[0].strip()
	
	fig_num = fig_fields[1].strip()
	
	if len(fig_fields) > 2:
		fig_desc = fig_fields[2].strip()
	else:
		fig_desc = ""
	# --> why did I do it the way below ?
	#fig_desc = fig_fields[2].strip().strip('"').strip()
	
	fig_filepath = os.path.join(dir, fig_filename)
	
	if not os.path.isfile(fig_filepath):
		return "Error: Plugin FIG_EXT: External metapost file not found."
	
	# read the mp file
	with open(fig_filepath, 'r') as f:
		mp = f.read()
	
	# process it
	process_metapost(subdir, fig_filename, mp)
	
	mp_filename = fig_filename.split('.')[0]
	
	# create name
	png_filename = mp_filename+'-'+fig_num+'.png'
	
	# create tag
	img_tag = IMG_TAG_FIG.format(alt=fig_desc, src=png_filename)
	desc_tag = DESC_TAG.format(n=fig_num, desc=fig_desc)
	full_tag = img_tag+desc_tag
	
	# PDF production
	if config.PRODUCE_PDF:
		eps_filename = mp_filename+'-'+fig_num+'.eps'
		img_tag_md = "\n\n!["+fig_desc+"]("+eps_filename+")\n\n"
	
	else:
		img_tag_md = ""
	
	# (debug-print)
	#print("full tag: ", full_tag)
	#print("img_tag_md: ", img_tag_md)
	
	# return
	return full_tag, img_tag_md
	
