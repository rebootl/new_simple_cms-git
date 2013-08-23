'''Module of new_simple_cms

Main processing functions.'''

# Imports
#
# python
import os
import glob
import subprocess

# global config variables
from config import *

# common functions
from .common import pandoc_final, pandoc_pipe_from_file, pandoc_pipe, extract_title_block, scan_doctype
from .plugin_handler import get_cdata, plugin_cdata_handler, back_substitute
from .math_handler import check_math, math_handler


# Functions
#
# (bad function name, this should be substitute and process plugins !!!)
def substitute_content(subdir, file_body):
	'''Substitute the plugin space AND process the plugin content.

Returning the substituted body and the plugin blocks.'''
	# look for plug-in content and
	# replace it by placeholders
	file_body_subst, cdata_blocks=get_cdata(file_body)
	
	# process the plug-in content
	if cdata_blocks != []:
		plugin_blocks=plugin_cdata_handler(subdir, cdata_blocks)
	
	else:
		plugin_blocks=[]
	
	return file_body_subst, plugin_blocks
	

def handle_math(subdir, page_body):
	'''Handle math content.

Returns the page body.'''
	#
	# quick check for math content
	has_math = check_math(page_body)
	
	# if there's process
	if has_math:
		# (debug-print)
		print("Math found!")
		page_body_m = math_handler(subdir, page_body)
		return page_body_m
	
	else:
		# (debug-print)
		print("No math found.")
		return page_body
	

def handle_post(post_body, tb_opts, subcontent_page):
	'''Handling for post type subcontent !

Returns the post body in HTML.'''
	#
	# generate the time line + edit form/link
	subcontent_page_name=subcontent_page.split('.')[0]
	
	post_html_template='''<div class="Post">
<div class="Timeline"><span class="Date">%s</span>
<span class="Time">%s
	<span class="EditLink">
		<a href="/cgi-bin/cgi_edit.py?post_filename=%s"><img src="/icons/edit-lucent_11px.png" title="Edit post..." alt="Edit Post- Button" style="width:11px;display:inline;" /></a>
</span></span>
</div>
%s
</div>'''
	
	# insert the values
	post_body_full=post_html_template % (tb_opts[2], tb_opts[3], subcontent_page_name, post_body)
	
	# concatenate (--> doing all above)
	#post_body_full=timeline_subst+'\n'+post_body+'\n'+closediv
	
	# return
	return post_body_full
	

def preprocess_page_group(subdir, page_group):
	'''Preprocess the pages and call the final output function.
(Doing this group wise. Every group contains the page and the corresponding subcontent.)

Returns the substituted main body.
And the plugin blocks and the title block as lists.'''
	
	dir=os.path.join(CONTENT_DIR, subdir)
	file_markdown=os.path.join(dir, page_group[0])
	
	## Read out the main page and title block:
	main_page_body, main_page_tb_vals=extract_title_block(file_markdown, REGULAR_TB_LINES)
	
	## Preprocess the subcontent:
	#
	# sort it
	subcontent_pages=page_group[1:]
	subcontent_pages.sort()
	subcontent_pages.reverse()
	
	for subcontent_page in subcontent_pages:
		subcontent_file=os.path.join(CONTENT_DIR, subdir, subcontent_page)
		
		## Get the subcontent type of this page:
		for subcontent_type in SUBCONTENT_TYPES:
			if subcontent_type in subcontent_page:
				page_type=subcontent_type
		
		## Read out the body and title block:
		## Special feature - include a custom title block !
		if page_type in INCLUDE_CUSTOM_TB:
			# call the extract titleblock function
			sub_page_body, sub_tb_vals=extract_title_block(subcontent_file, CUSTOM_TB_LINES)
		else: sub_page_body, sub_tb_vals=extract_title_block(subcontent_file, REGULAR_TB_LINES)
		
		## Handling has to be defined for every subcontent type here!
		##  + A handler function has to be written for it (if necessary) !
		##  By default the subcontent will simply be appended to the main page body,
		#    w/o additional preprocessing !
		#
		# post type
		if page_type == 'post':
			sub_page_ready=handle_post(sub_page_body, sub_tb_vals, subcontent_page)
		
		# additional types here
		# ...
		
		else:
			sub_page_ready=sub_page_body
		
		# concatenate to the main page
		main_page_body=main_page_body+'\n'+sub_page_ready
	
	# substitute and process the plugin content
	main_page_body_subst, plugin_blocks=substitute_content(subdir, main_page_body)
	
	## Preprocess math content
	# similar to plugins math content is handled here by my own functions
	# (see the math_handler module)
	if PROCESS_MATH:
		main_page_body_subst_m = handle_math(subdir, main_page_body_subst)
		return main_page_body_subst_m, plugin_blocks, main_page_tb_vals
	
	else:
		return main_page_body_subst, plugin_blocks, main_page_tb_vals
	

### New function for CGI frontend, construct pages_struct only for a page.
#   Used to only refersh a single page. (But with it's subontent !)
#
#   Could later be used to refresh a single page from CLI too.
#   (Therefor putting it here!) - doing this
#
##
def process_page(page, subdir):
	'''Construct pages_struct only for a page.
Used to only refersh a single page. (But with it's subontent !)

Returns the pages_struct.'''
	
	dir=os.path.join(CONTENT_DIR, subdir)
	dir_content=os.listdir(dir)
	
	## Check if there's an index file:
	if glob.glob(os.path.join(dir, '*listing*')):
		# checking for listing page first
		print("Listing file found, returning...")
		return []
	elif glob.glob(os.path.join(dir,'*index*')):
		pass
	else:
		# if no index file is found the directory
		#  should be published as listing
		#  for now just exit
		print("No index file found, returning...")
		return []
	
	# find the subcontent
	## Get all .markdown files:
	markdown_filelist=[]
	for file in dir_content:
		if file.endswith('.markdown'):
			markdown_filelist.append(file)
	
	# get the main page name
	main_page_name=page.split('.')[0]
	
	subcontent_pages=[]
	for file in markdown_filelist:
		for type in SUBCONTENT_TYPES:
			if type in file and main_page_name in file:
				if not file in subcontent_pages:
					subcontent_pages.append(file)
	
	pages_struct=[[page]+subcontent_pages]
	return pages_struct
	

## For every directory in content do:
def process_dir(subdir):
	'''Get the files for processing, group them and call the preprocess function.
Doing this directory wise, for the directories in content, incl. '.'.

Returns the pages_struct. A nested list.'''
	dir=os.path.join(CONTENT_DIR, subdir)
	dir_content=os.listdir(dir)
	
	## Check if there's an index file:
	if glob.glob(os.path.join(dir, '*listing*')):
		# checking for listing page first
		print("Listing file found, returning...")
		return []
	elif glob.glob(os.path.join(dir,'*index*')):
		pass
	else:
		# if no index file is found the directory
		#  should be published as listing
                #  for now just exit
                print("No index file found, returning...")
                return []
	
	## Get all .markdown files:
	markdown_filelist=[]
	for file in dir_content:
		if file.endswith('.markdown'):
			markdown_filelist.append(file)
	
	## Filter main and subcontent pages:
	main_pages=[]
	subcontent_pages=[]
	for file in markdown_filelist:
		for type in SUBCONTENT_TYPES:
			### ---> this function is erroneaus, cause it would cause
			###       multiple appends if there is more than one type !!! <---
			### it does... removing the types !
			# corrected by additional check
			if not type in file:
				if not file in main_pages:
					main_pages.append(file)
			else:
				if not file in subcontent_pages:
					subcontent_pages.append(file)
	
	# debug-info
	#print(main_pages)
	
	## Group the pages and their subcontent:
	#   Whereas pages_struct has the form:
	# [['main-page','subcont','subcont',etc.],[main-page,subcont,subcont,etc.],etc.]
	pages_struct=[]
	for idx, page in enumerate(main_pages):
		pages_struct.append([page])
		# extract the page name
		page_name=page.split('.')[0]
		for file in subcontent_pages:
			if page_name in file:
				pages_struct[idx].append(file)
	
	# debug-info
	print('Pages struct:', pages_struct)
	#for group in pages_struct:
	#	for file in group:
	#		print(file.split('.')[0])
	# return
	return pages_struct
	

def prepare_final(subdir, page_group, title_block_vals, main_menu, section_menu_list, body_doctype):
	'''Preparations for final output.

Returns options for final Pandoc run and output path.'''
	#
	# out file, should be html
	page_name=page_group[0].split('.')[0]
	out_filepath=os.path.join(PUBLISH_DIR, subdir, page_name+'.html')
	
	final_opts=[]
	
	# set the doctype
	if body_doctype == 'transitional':
		final_opts.append('--variable=doctype:'+DOCTYPE_STRING_TRANSITIONAL)
	else:
		final_opts.append('--variable=doctype:'+DOCTYPE_STRING_STRICT)
	
	# main menu
	final_opts.append('--variable=main-menu:'+main_menu)
	
	# section menu
	# pandoc bug, reversed order
	section_menu_list.reverse()
	for menu_line in section_menu_list:
		final_opts.append('--variable=section-menu-line:'+menu_line)
	
	# title block
	for index, tb_value in enumerate(title_block_vals):
		final_opts.append('--variable='+REGULAR_TB_LINES[index]+':'+tb_value)
	
	# include a table of content
	final_opts.append('--toc')
	final_opts.append('--toc-depth='+TOC_DEPTH)
	
	# set the final template
	final_opts.append('--template='+MAJOR_TEMPLATE)
	
	# (debug-info)
	#print("Final opts (section menu):", final_opts)
	
	return final_opts, out_filepath
	
