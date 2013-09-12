'''Module of new_simple_cms

Directory listing functions.
'''

# Imports
#
# python
import os
from datetime import datetime

# global config variables
import config

# common functions
from .common import pandoc_final, pandoc_pipe_from_file, pandoc_pipe, scan_doctype


# Functions

def get_listing_page(subdir):
	'''Return listing page.'''
	listing_page_md=''
	for file in os.listdir(os.path.join(config.CONTENT_DIR, subdir)):
		if 'listing' in file:
			listing_page_md=file
	return listing_page_md
	

def get_size_n_date_nice(item_path):
	'''Return size and date of a file.'''
	## Size:
	# get the size
	size_bytes=os.path.getsize(item_path)
	
	# make it nice
	if size_bytes >= 1000*1000 :
		size_mb=round(size_bytes/(1000*1000), 3)
		size_str=str(size_mb)+' MB'
	elif size_bytes >= 1000 :
		size_kb=size_bytes/1000
		size_str=str(size_kb)+' kB'
	else:
		size_str=str(size_bytes)+' B'
	
	## Date:
	# get the date
	mdate_s=os.path.getmtime(item_path)
	
	# format it
	mdate_f=datetime.fromtimestamp(mdate_s)
	mdate_str=mdate_f.strftime('%a %Y-%m-%d %H:%M UTC'+config.UTC_DELTA)
	
	return size_str, mdate_str
	


def gen_listing_table_entries(subdir, listing_page_md):
	'''Generate entries for a listing table.

Returning the table as string.'''
	#
	# get the dir content
	dir=os.path.join(config.CONTENT_DIR, subdir)
	dir_content=os.listdir(dir)
	
	# filter out the listing page
	remove_list=[]
	for item in dir_content:
		if 'listing' in item:
			remove_list.append(item)
	
	for item in remove_list:
		dir_content.remove(item)
	
	## Make the table lines:
	# sort the content
	dir_content.sort()
	
	table_lines=[]
	for item in dir_content:
		item_path=os.path.join(dir, item)
		
		# define the table line
		#  variables: class_str_cpl title_str_cpl href name size date
		table_line_str='<tr><td><a {} {} href="{}">{}</a></td><td align="right">{}</td><td align="right">{}</td></tr>'
		
		class_str='class="{}"'
		title_str='title="{}"'
		
		# --> the entire handling below is messy and should be improved/simplified !
		
		# separate handling for links needed !
		if os.path.islink(item_path):
			# add a title
			target=os.path.realpath(item_path)
			link_title='Originally a link to: '+target
			
			## if it exists, add class continue normal handling:
			if os.path.exists(item_path):
				class_str_cpl=class_str.format(config.LINK_CLASS_NAME)
				title_str_cpl=title_str.format(link_title)
				pass
			
			## if not, handle it completely separate!
			else:
				# set class and title
				class_str_cpl=class_str.format(config.BROKENLINK_CLASS_NAME)
				title_str_cpl=title_str.format('')
				
				# set size to --
				nosize_str="--"
				
				# set date to BROKENLINK
				broken_str="BROKENLINK"
				
				## Make the line:
				table_line_subst=table_line_str.format(class_str_cpl, title_str_cpl, item, item, nosize_str, broken_str)
				
				table_lines.append(table_line_subst)
				
				# continue with the next item
				continue
			
		
		# separate handling for directories needed
		if os.path.isdir(item_path) and not os.path.islink(item_path):
			class_str_cpl=class_str.format(config.DIR_CLASS_NAME)
			title_str_cpl=''
			item_href=(os.path.join(item, 'listing.html'))
			item_name=item+'/'
		
		elif os.path.isdir(item_path) and os.path.islink(item_path):
			class_str_cpl=''
			title_str_cpl=''
			item_href=item
			item_name=item+'/'
			
		elif os.path.islink(item_path):
			item_href=item
			item_name=item
		else:
			class_str_cpl=''
			title_str_cpl=''
			item_href=item
			item_name=item
		
		# get size and date
		size_str, date_str=get_size_n_date_nice(item_path)
		
		## Make the line:
		table_line_subst=table_line_str.format(class_str_cpl, title_str_cpl, item_href, item_name, size_str, date_str)
		
		table_lines.append(table_line_subst)
	
	## Make the table:
	
	# only making the lines here, the table is defined in the template
	# make the lines
	table_entries_str=''
	for line in table_lines:
		table_entries_str=table_entries_str+line+'\n'
	
	#return listing_table
	return table_entries_str
	


# --> this is done in new_simple_cms, doesn't work here
#def getset_parent_dir(subdir):
#	# get/set the parent dir (for the path line)
#	global LISTING_PARENT_DIR
#	if LISTING_PARENT_DIR == '' :
#		LISTING_PARENT_DIR=subdir
#	elif LISTING_PARENT_DIR in subdir:
#		pass
#	else: LISTING_PARENT_DIR=subdir
	


def gen_listing_path_items(subdir, parent_dir, listing_page_md):
	'''Generate listing path links (As list.)'''
	# generate the path
	rel_path=os.path.relpath(subdir, parent_dir)
	
	# (debug-info)
	#print('Rel path:', rel_path)
	
	path_j=os.path.join(os.path.basename(parent_dir), rel_path)
	
	# renice it
	path=os.path.relpath(path_j)
	
	# (debug-info)
	#print('Path:', path)
	
	# for each directory in path we create a (relative) link
	path_dirs=path.split('/')
	path_dirs.reverse()
	link_items=[]
	for index, dir in enumerate(path_dirs):
		link_line_str='<a class="{}" href="{}">{}</a>'
                
		link_ref=os.path.join(index*'../', 'listing.html')
		link_name=dir
		
		link_line_subst=link_line_str.format(config.DIR_CLASS_NAME, link_ref, link_name)
		link_items.append(link_line_subst)
	
	link_items.reverse()
	
	# (debug-info)
	#print('Link lines:', link_items)
	
	return link_items
	


def prepare_final_listing(subdir, listing_path_items, listing_table_entries_str, main_menu, title_block_vals, listing_body_doctype):
	'''As processing.prepare_final.'''
	#
	# pandoc out
	pandoc_out_filename='listing.html'
	pandoc_out=os.path.join(config.PUBLISH_DIR, subdir, pandoc_out_filename)
	
	final_opts=[]
	
	# set the doctype
	if listing_body_doctype == 'transitional':
		final_opts.append('--variable=doctype:'+config.DOCTYPE_STRING_TRANSITIONAL)
	else:
		final_opts.append('--variable=doctype:'+config.DOCTYPE_STRING_STRICT)
	
	# path line
	# pandoc-bug reversed order
	listing_path_items.reverse()
	
	for item in listing_path_items:
		final_opts.append('--variable=listing-path-line:'+item)
	
	# listing table
	final_opts.append('--variable=listing-table-entries:'+listing_table_entries_str)
	
	# main menu
	final_opts.append('--variable=main-menu:'+main_menu)
	
	# title block opts
	for index, tb_value in enumerate(title_block_vals):
		final_opts.append('--variable='+config.REGULAR_TB_LINES[index]+':'+tb_value)
	
	# set the final template
	final_opts.append('--template='+config.LISTING_TEMPLATE)
	
	return final_opts, pandoc_out
