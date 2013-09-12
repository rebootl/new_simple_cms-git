'''Module of new_simple_cms.py.

Recursive creation of a dynamic website menu based on a
directory structure.'''

# Imports
#
# python modules
import os

# import global config variables
import config

# and common functions
from .common import pandoc_pipe, get_index_path


# Functions

def make_folders_struct(active_dir):
	# replacement for the way too complicated recurse_dir function (above, removed).
	run_count=0
	for dir, dirs, files in os.walk(config.CONTENT_DIR):
		relpath=os.path.relpath(dir, config.CONTENT_DIR)
		if run_count == 0 :
			folders_struct=[dirs]
		
		elif relpath in active_dir:
			# check for listing page
			index_path=get_index_path(relpath)
			if not index_path.endswith('listing.html'):
				# (debug-info)
				#print('Dir:', dir)
				#print('Appending dirs:', dirs)
				full_names=[]
				dir_path=os.path.relpath(dir, config.CONTENT_DIR)
				for subdir in dirs:
					full_name=os.path.join(dir_path, subdir)
					full_names.append(full_name)
				folders_struct.append(full_names)
				# (debug-info)
				#print('Appending dirs nice:', full_names)
		
		run_count+=1
		# (debug-info)
		#print('Dir:', dir)
		#print('Dirs:', dirs)
	
	# remove the last entry if empty
	if folders_struct[-1] == []:
		del folders_struct[-1]
	
	# (debug-info)
	#print('Folders struct:', folders_struct)
	
	return folders_struct
	


def make_submenus_struct(folders_struct, active_dir, active_page):
	submenus_struct=[]
	
	# insert the home
	folders_struct[0].insert(0, config.HOME_NAME)
	
	# make custom menu order if set
	if config.CUSTOM_MENU_ORDER != []:
		folders_struct[0]=config.CUSTOM_MENU_ORDER
		
	# sort the items from second level on
	for item in folders_struct[1:]:
		item.sort()
	
	for dir_group in folders_struct:
		# lines has to be cleared here !!
		lines=[]
		
		# (debug-info)
		#print('Dir group:', dir_group)
		
		for dir in dir_group:
			# (debug-info)
			#print('Dir:', dir)
			
			# define the link line
			link_line='<a {} href="{}">{}</a>'
			
			if dir == config.HOME_NAME:
				# settings for home
				index_path='./index.html'
				
				name=config.HOME_NAME
				link='index.html'
				
			else:	
				# get the index page and define the line entries
				# (index_page returns the path + pagename as html)
				index_path=get_index_path(dir)
				
				# add a trailing / for listing dirs
				if index_path.endswith('listing.html'):
					name=os.path.basename(dir)+'/'
				else:
					name=os.path.basename(dir)
				link=index_path
			
			# make the html extension
			active_page_html=active_page.split('.')[0]+'.html'
			active_path=os.path.join(active_dir, active_page_html)
			
			# include the ../'s for subdirs
			if active_dir != '.':
				for i in range(len(active_dir.split('/'))):
					link=os.path.join('../', link)
			
			# (debug-info)
			#print('Active path:', active_path)
			#print('Index path:', index_path)
			#print('Active dir:', active_dir)
			
			# if the page is active, include a CSS class
			class_type=''
			if active_dir == os.path.dirname(index_path):
				# exclude the hidden pages
				for hidden_page_name in config.HIDDEN_PAGE_NAMES:
					if not hidden_page_name in active_page:
					### --> this is erroneous, causing multiple appends,
					###      if there are multiple hidden pages...
						
						# anyways using a string now
						class_type='class="'+config.ACTIVE_CLASS_NAME+'"'
			
			# listing dirs should stay active, when browsing subdirs...
			elif index_path.endswith('listing.html'):
				if os.path.dirname(index_path) in active_dir:
					class_type='class="'+config.ACTIVE_CLASS_NAME+'"'
			
			# set the strings (unnecessary...)
			link_name=name
			link_ref=link
			
			## Make the line.
			line=link_line.format(class_type, link_ref, link_name)
			lines.append(line)
		
		submenus_struct.append(lines)
	
	# (debug-info's)
	#for item in submenus_struct:
	#	print(item)
	#print("Submenus struct:", submenus_struct)
	
	return submenus_struct, folders_struct
	


def arrange_menu(folders_struct, submenus_struct):
	### rewriting the erroneous arrage_submenus function (above, removed)
	
	for level, menu_group in enumerate(submenus_struct):
		secondlast_submenu='<ul>\n'
		for index, item in enumerate(submenus_struct[-1-level]):
			item_str='<li>'+item
			if level == 0 :
				secondlast_submenu=secondlast_submenu+item_str+'</li>\n'
			elif folders_struct[-1-level][index] in folders_struct[-level][0]:
				secondlast_submenu=secondlast_submenu+item_str+last_submenu+'</li>\n'
			else:
				secondlast_submenu=secondlast_submenu+item_str+'</li>\n'
		secondlast_submenu=secondlast_submenu+'</ul>'
		last_submenu=secondlast_submenu
	
	# (unnecessary...)
	menu_cpl=last_submenu
	
	# (debug-info)
	#print('Menu markdown:', menu_markdown)
	
	# (debug-info)
	#print('Menu html:', menu_html)	
	
	return menu_cpl
	


def generate_main_menu(active_dir, active_page):
	folders_struct=make_folders_struct(active_dir)
	
	# (debug-info)
	#print('Folders struct:', folders_struct)
	
	submenus_struct, folders_struct=make_submenus_struct(folders_struct, active_dir, active_page)
	
	# (debug-info)
	#print('Folders struct:', folders_struct)
	#print('Submenus struct:', submenus_struct)
	#for item in submenus_struct:
	#	print(item)
	
	menu=arrange_menu(folders_struct, submenus_struct)
	
	# (debug-info)
	#print(menu)
	return menu
	


