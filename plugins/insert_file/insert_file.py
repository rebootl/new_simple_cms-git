#!/usr/bin/python
#
# Plugin for new_simple_cms.
#
# Insert a file content. Either as text or as specified code block.
#
# This one will simply use pandoc to format the code blocks!
#
# CDATA syntax:
#
# <![INSERTFILE[type, filename]]>
#
# Where _type_ can be text, or any code type pandoc understands (see pandoc --version).
# And _filename_ can be an either be a relative path, starting in the directory the plugin is 
#  used. Or an absolute path.
#
##

## Imports:
#
# python
import os

# global config variables
from config import *

# common functions
from modules.common import pandoc_pipe

## Plugin config variables:
INSERT_FILE_CLASS='InsertFile'


def insert_file(subdir, plugin_in):
	# get the content type and path or filename
	fields=plugin_in.split(',')
	type=fields[0]
	
	file_in=fields[-1].strip()
	
	# find out where the file lies
	if not os.path.isabs(file_in):
		filepath=os.path.join(CONTENT_DIR, subdir, file_in)
	
	else:
		filepath=file_in
	
	# (debug-info)
	#print('Filepath:', filepath)
	
	# check if it exists
	if os.path.isfile(filepath):
		print("Inserting file:", filepath)
		pass
	else:
		# could make a nicer html error here...
		# and maybe a try/except statement would be better but (?)
		file_not_found_error="INSERTFILE plugin error: File ("+filepath+") not found."
		print(file_not_found_error)
		return file_not_found_error
	
	# read the file
	file_op=open(filepath, 'r')
	file_content=file_op.read()
	file_op.close()
	
	# extract additional fields
	add_fields=''
	if len(fields) > 2:
		for field in fields[1:-1]:
			add_fields=' '+field.strip()+add_fields
	
	# append markdown code syntax and type and additional fields
	markdown_code_pre='~~~ {.'+type+add_fields+' .'+INSERT_FILE_CLASS+'}'
	markdown_code_post='~~~'
	
	file_content_md=markdown_code_pre+'\n'+file_content+'\n'+markdown_code_post
	
	# process through pandoc
	file_content_html=pandoc_pipe(file_content_md, [])
	
	# insert a title block (table, already html formatted)
	filename=os.path.basename(filepath)
	dir_path=os.path.dirname(file_in)
	if dir_path == '':
		dir_path='.'
	title_line='<table class="InsertFileTitle"><tr><td class="Titlefield">Filename:</td><td class="Textfield" title="Inserted from: '+dir_path+'">'+filename+'</td></tr></table>'
	
	file_content_html_title=title_line+'\n'+file_content_html
	
	return file_content_html_title
	
