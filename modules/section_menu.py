'''Module of new_simple_cms

Creation of a simple section menu. A section menu includes all main pages
within a directory.'''

# Imports
#
# python modules
import os

# import global config variables
import config

# and common functions
from .common import pandoc_pipe, get_index_path, extract_title_block_only


# Functions

def generate_section_menu(subdir, active_page):
	# always set the index page as first
	# first check if there are other pages in the subdir
	
	dir=os.path.join(config.CONTENT_DIR, subdir)
	
	# get the remaining pages
	pages=[]
	files=os.listdir(dir)

	for file in files:
		if file.endswith(config.MD_EXT):
			pages.append(file)
	
	# make a remove list
	remove_list=[]
	# remove the subcontents
	for file in pages:
		# only using one type of subcontent by now !
		for type in config.SUBCONTENT_TYPES:
			if type in file:
				remove_list.append(file)
	
	# remove hidden pages (e.g. a page you don't want to show up in the menu)
	for file in pages:
		for name in config.HIDDEN_PAGE_NAMES:
			if file.__contains__(name):
				remove_list.append(file)
	
	# remove the pages
	for item in remove_list:
		pages.remove(item)
	
	# sort and make index first
	#  (Keep an eye on that one, I think it should work fine,
	#   but it may not be best.)
	pages.sort()
	for page in pages:
		if page.__contains__('index'):
			pages.remove(page)
			pages.insert(0, page)
	# (debug-info)
	#print("Pages (section menu):", pages)
	
	# if no other pages are found, return
	#  (I don't want a section menu for only one page.)
	if len(pages) <= 1 : return []
	
	# (debug-info)
	#print("Active page:", active_page)
	#print("Pages:", pages)
	
	# get the page titles
	titles=[]
	for page in pages:
		filepath=os.path.join(config.CONTENT_DIR, subdir, page)
		title=extract_title_block_only(filepath, ['title'])
		titles.append(title[0])
	
	# (debug-info)
	#print("Titles (section menu):", titles)
	
	# make .html endings
	for index, page in enumerate(pages):
		pages[index]=page.split('.')[0]+'.html'
	
	active_page_html=active_page.split('.')[0]+'.html'
	
	# make the line variables
	lines=[]
	for index, page in enumerate(pages):
		class_str='class="{}"'
		if page == active_page_html:
			class_str_cpl=class_str.format(config.ACTIVE_CLASS_NAME)
		else:
			class_str_cpl=class_str.format('')
		
		# define the line here
		# --> could be defined in the config...
		link_line_str='<a {} href="{}">{}</a>'
		
		# substitution
		link_line_subst=link_line_str.format(class_str_cpl, page, titles[index])
		
		lines.append(link_line_subst)
	
	# (debug-info)
	#print("Lines (section menu):", lines)
	
	return lines
	

