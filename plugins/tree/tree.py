#!/usr/bin/python
'''plugin for new_simple_cms

Insert a clickable directory tree structure.

Using tree to generate the tree.
Probably using a little javascript to edit the links to use listing.html.

Syntax:

[[ TREE ][ directory, tree-options ]]

Where directory can be a relative path, starting in the current content
subdirectory, or an absolute path.

And tree-options are additional tree command line options.
'''
# This file is part of new_simple_cms
#--------------------------------------------------------------------------------
#
# Copyright 2013 Cem Aydin
#
#--------------------------------------------------------------------------------
# See new_simple_cms.py for more information.

## Imports:
#
# python
import os
import subprocess

# global config variables
import config

# common functions
#from modules.common import pandoc_pipe

## Plugin config variables:
TREE_CLASS_NAME='Tree'
FOOTER_TEXT='Modified output and style for this website.'


def tree_pipe(dir, add_opts):
	## Create a tree pipe
	#
	# the command
	tree_command=['tree']
	base_options=['-a', dir]
	
	cmd=tree_command+base_options+add_opts
	
	# the pipe
	proc=subprocess.Popen(cmd, stdout=subprocess.PIPE)
	output=proc.communicate()
	output=output[0].decode('utf-8')
	
	return output
	

#def tree_pipe_ascii(dir):
#	cmd = ['tree', '-a', '--charset', 'ascii', dir]
#	
#	proc=subprocess.Popen(cmd, stdout=subprocess.PIPE)
##	stdout, stderr=proc.communicate()
#	output = stdout.decode('ascii')
#	
#	return output
	

def tree(subdir, plugin_in):
	# read the fields
	fields=plugin_in.split(',')
	directory_in=fields[0]
	
	add_fields=[]
	for item in fields[1:]:
		add_fields.append(item.strip())
		
	# find the dir
	if not os.path.isabs(directory_in):
		directory_real=os.path.join(config.CONTENT_DIR, subdir, directory_in)
	
	else:
		directory_real=directory_in
	
	# (debug-info)
	#print('Filepath:', filepath)
	
	# check if it exists
	if os.path.isdir(directory_real):
		print("Inserting tree for:", directory_real)
		pass
	else:
		# could make a nicer html error here...
		# and maybe a try/except statement would be better but (?)
		file_not_found_error="TREE plugin error: Directory ("+directory_real+") not found."
		print(file_not_found_error)
		return file_not_found_error, file_not_found_error
	
	# run tree
	title = directory_in
	# options: -C (colorize) -H (header)
	html_opts = ['-C', '--charset', 'utf8', '-H', title ]
	tree_html_out=tree_pipe(directory_real, html_opts)
	
	# (debug-info)
	#print(tree_html_out)
	
	## Format the tree html output.
	# correct output to XHTML replacing <br> by <br /> and <hr> by <hr />
	tree_html_out=tree_html_out.replace('<br>', '<br />')
	tree_html_out=tree_html_out.replace('<hr>', '<hr />')
	
	# remove the first 29 lines (html, head, style)
	tree_html_lines=tree_html_out.split('\n')
	del tree_html_lines[0:29]
	
	# remove the last two lines (/body, /html, empty line(?))
	del tree_html_lines[-1]
	del tree_html_lines[-1]
	del tree_html_lines[-1]
	
	# add a footer
	footer='<hr /><p class="VERSION">'+FOOTER_TEXT+'</p>'
	tree_html_lines.append(footer)
	
	# enclose by a div
	tree_div_start='<div class="'+TREE_CLASS_NAME+'">'
	tree_div_end='</div>'
	
	tree_html_lines.insert(0, tree_div_start)
	tree_html_lines.append(tree_div_end)
	
	# join back
	tree_html_formatted='\n'.join(tree_html_lines)
	
	# (debug-info)
	#print(tree_html_lines)
	
	if config.PRODUCE_PDF:
		# trying to insert HTML
		# --> _bad_, latex doesn't understand utf8/unicode (? what's the difference ?)
		# ==> here we need an ascii output of tree, _nice_
		#tree_html_formatted_md = tree_html_formatted
		ascii_opts = [ '--charset', 'ascii' ]
		tree_ascii_out = tree_pipe(directory_real, ascii_opts)
		
		# replace top level directory
		tree_ascii_lines = tree_ascii_out.split('\n')
		del tree_ascii_lines[0]
		tree_ascii_lines.insert(0, directory_in)
		tree_ascii_mod = '\n'.join(tree_ascii_lines)
		
		# wrap it in markdown code delimiters + title
		md_pre = '\nDirectory Tree\n\n~~~~\n'
		md_post = '\n~~~~\n\n'
		tree_ascii_out_md = md_pre+tree_ascii_mod+md_post
		
	else:
		tree_ascii_out_md = ""
	
	return tree_html_formatted, tree_ascii_out_md
	
