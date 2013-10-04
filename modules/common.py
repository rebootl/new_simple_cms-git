'''module of new_simple_cms

Common functions.
(These get imported by the other modules!)

- Pandoc processing pipes
- Extract title block
- ...
'''
# This file is part of new_simple_cms
#--------------------------------------------------------------------------------
#
# Copyright 2013 Cem Aydin
#
#--------------------------------------------------------------------------------
# See new_simple_cms.py for more information.

# Imports
#
# python
import os
import subprocess
import re

# global config variables
import config


# Functions

def scan_doctype(page_body):
	'''Scan the page body and set the doctype accordingly
(Only scanning for iframes atm, more tags could be added.)
Return doctype.'''
	#
	# iframes
	re_iframe=re.compile('<iframe.+?></iframe>', re.DOTALL)
	re_search=re_iframe.search(page_body)
	
	if re_search != None:
		doctype='transitional'
	else:
		doctype='strict'
	
	return doctype
	


def get_dirs(refresh_dir):
	'''Get the subdirs for processing.

Returns a list of subdirs w/o CONTENT_DIR.'''
	
	subdirs=[]
	# trying some os walk opts
	for dir, dirs, files in os.walk(os.path.join(config.CONTENT_DIR, refresh_dir)):
		# (debug-info's)
		#print('Dir:', dir)
		#print('Dirs:', dirs)
		#print('Files:', files)
		
		# remove the CONTENT_DIR from path
		subdir=os.path.relpath(dir, config.CONTENT_DIR)
		
		subdirs.append(subdir)
	
	# (debug-info)
	#print('Subdirs:', subdirs)
	
	return subdirs
	


def copy_file(subdir, file):
	'''Using cp command to copy a file.

Using the CONTENT_DIR and PUBLISH_DIR variables.'''
	#
	# input file
	in_file=os.path.join(config.CONTENT_DIR, subdir, file)
	# output directory
	out_dir=os.path.join(config.PUBLISH_DIR, subdir)
	# using cp -u (update, cp only if newer) 
	#  -d (preserve links --> links are handled separately now)
	cp_command=['cp', '-u', in_file, out_dir]
	
	proc=subprocess.Popen(cp_command)
	

def copy_file_abs(inpath, out_dir):
	'''Call copy w/o preset directories.
(Not recursive.)
--> shutil.copy could be used for this.'''
	# using cp -u
	cp_command=['cp', '-u', inpath, out_dir]
	
	proc=subprocess.Popen(cp_command)
	

def make_linkfile(subdir, link):
	'''Make a file for links.'''
	linkpath=os.path.join(config.CONTENT_DIR, subdir, link)
	
	out_dir=os.path.join(config.PUBLISH_DIR, subdir)
	
	targetpath=os.path.realpath(linkpath)
	fileinfo="This file was created by the website CMS new_simple_cms (powered by Python)."
	if not os.path.exists(linkpath):
		# broken link
		text='''Originally this was a link to: %s
The link was BROKEN on the website generation system.

%s''' % (targetpath, fileinfo)
	elif os.path.isdir(linkpath):
		# directories
		text='''Originally this was a link to the directory: %s

%s''' % (targetpath, fileinfo)
	else:
		# good link
		text='''Originally this was a link to: %s

%s

Target file content:
''' % (targetpath, fileinfo)
		
		# include the linked file content (!), hehe
		## try except for binary
		try:
			target_open=open(targetpath, 'r')
			target_content=target_open.read()
			target_open.close()
			text=text+target_content
		except UnicodeDecodeError:
			target_open.close()
			text=text+"Could not decode content... probably BINARY."
	
	outfile=open(os.path.join(out_dir, link), 'w')
	outfile.write(text)
	outfile.close()
	


def copy_remaining_content(subdir):
	'''Copy the remaining folder content.'''
	dir=os.path.join(config.CONTENT_DIR, subdir)
	
	# get the dir content
	filelist=os.listdir(dir)
	
	# filter out dirs
	remove_list=[]
	for file in filelist:
		if os.path.isdir(os.path.join(config.CONTENT_DIR, subdir, file)):
			remove_list.append(file)
	
	# filter out markdown files
	for file in filelist:
		if file.endswith(config.MD_EXT):
			remove_list.append(file)
	
	# the markdown backup files created by the cgi frontend
	for file in filelist:
		if file.endswith(config.MD_EXT+'~'):
			remove_list.append(file)
	
	# more filters might be specified here
	# ...

	for item in remove_list:
		filelist.remove(item)
	
	# (debug-print)
	#print(filelist)
	
	# call copy function
	for file in filelist:
		copy_file(subdir, file)
	


def copy_listing_content(subdir):
	'''Copy the folder content of listing pages
Different filtering than copy_remaining_content.
(For listing pages we want everything exept listing.markdown.)
Added exceptionally special handling for links...'''
	
	dir=os.path.join(config.CONTENT_DIR, subdir)
	
	# get the dir content
	filelist=os.listdir(dir)
	
	remove_list=[]
	link_list=[]
	# filter out links and add them to a separate list
	for file in filelist:
		if os.path.islink(os.path.join(config.CONTENT_DIR, subdir, file)) and os.path.isdir(os.path.join(config.CONTENT_DIR, subdir, file)):
			link_list.append(file)
		elif os.path.islink(os.path.join(config.CONTENT_DIR, subdir, file)) and not os.path.isdir(os.path.join(config.CONTENT_DIR, subdir, file)):
			link_list.append(file)
			remove_list.append(file)
	
	# filter out dirs
	for file in filelist:
		if os.path.isdir(os.path.join(config.CONTENT_DIR, subdir, file)):
			remove_list.append(file)
	
	# filter out the listing page
	for file in filelist:
		if file.endswith(config.MD_EXT) and 'listing' in file:
			remove_list.append(file)
	
	# more filters might be specified here
	# ...
	
	for item in remove_list:
		filelist.remove(item)
	
	# call copy function
	for file in filelist:
		copy_file(subdir, file)
	
	# (debug-print)
	#print("Link list:", link_list)
	# special treatment for links
	for link in link_list:
		make_linkfile(subdir, link)
	


def write_out(content, outfile):
	'''Write out content to file.'''
	out_dir=os.path.dirname(outfile)
	if os.path.isdir(out_dir):
		pass
	else: os.makedirs(out_dir)
	
	outfile_o=open(outfile, 'w')
	outfile_o.write(content)
	outfile_o.close()
	


def pandoc_final(opts, outfile, template):
	'''Get's all content variables and writes the page to it's final destination.'''
	#
	# check/create out directory
	out_dir=os.path.dirname(outfile)
	if os.path.isdir(out_dir):
		pass
	else:
		os.makedirs(out_dir)
	# the pandoc command
	pandoc_command=['pandoc', '-o', outfile, '--template', template]
	args=pandoc_command+opts
	# the subprocess call
	# (at the moment the stdin pipe is empty cause all the content get's passed
	#  by variables, I think I set it to pipe cause otherwise it expects user input)
	proc=subprocess.Popen(args, stdin=subprocess.PIPE)
	proc.communicate()
	


def pandoc_pipe_from_file(infile, opts):
	'''Create a pandoc pipe reading from a file and returning the output.'''
	#
	# the pandoc command
	pandoc_command=['pandoc', infile]
	args=pandoc_command+opts
	# the pipe
	proc=subprocess.Popen(args, stdout=subprocess.PIPE)
	#output=proc.stdout.read()
	# (using communicate instead)
	output=proc.communicate()
	# output returns a byte obj, try converting it to a string --> works like a charm !
	# output[0] is stdout, output[1] would be stderr !
	output=output[0].decode('utf-8')
	return output
	


def pandoc_pipe(content, opts):
	'''Create a pandoc pipe reading from a variable and returning the output.'''
	#
	# the pandoc command
	pandoc_command=['pandoc']
	# adding math support
	# (done by own functions)
	#opts.append('--gladtex')
	args=pandoc_command+opts
	# the pipe
	proc=subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	input=content.encode()
	output=proc.communicate(input=input)
	
	output=output[0].decode('utf-8')
	return output
	


def extract_title_block(file_markdown, title_block_lines):
	'''Simple extraction of title block from .markdown file.
(Doing this manually cause I want an additional line for the time !
And I don't want to write a temp file, and when using stdin, pandoc
seems not to evaluate the title block, therefor doing it here.)

Returning values as already formatted pandoc options.
+ Returning the file body w/o the title block for further processing.'''
	#
	# lines
	#title_block_lines=CUSTOM_TB_LINES
	# setting these above gives greater flexibility
	
	# open the file and read the lines
	file_op=open(file_markdown, 'r')
	file_lines=file_op.readlines()
	file_op.close()
	# succesively get the values and remove the lines
	title_block=[]
	#title_block_vals={}
	for linenumber, linename in enumerate(title_block_lines):
		full_line=file_lines[0]
		if full_line.startswith('%'):
			text=' '.join(full_line.split(' ')[1:]).rstrip()
			title_block.append(text)
			#title_block_vals[linename]=text
			# not creating opts here, that's odd...
			#title_block_opts.append('--variable='+linename+':'+text)
			del file_lines[0]
	
	# join the lines
	file_body=''.join(file_lines)
	# (debug-info)
	#print('File Body:', file_body)
	
	# return
	return file_body, title_block
	# evtl. future use of vals
	#return file_body, title_block_opts, title_block_vals
	


def extract_title_block_only(file, tb_lines):
	'''Extraction of title block from .markdown file.

Used for the section menu generation.
(Therefor it makes no sense to return the content.)

Returning title block lines as list.'''
	#
	# open the post and read the lines
	file_op=open(file, 'r')
	file_lines=file_op.readlines()
	file_op.close()
	# succesively get the values and remove the lines
	title_block=[]
	for linenumber, linename in enumerate(tb_lines):
		full_line=file_lines[0]
		if full_line.startswith('%'):
			text=' '.join(full_line.split(' ')[1:]).rstrip()
			title_block.append(text)
			del file_lines[0]
	
	# join the lines
	#post=''.join(post_lines)
	
	# return
	return title_block
	


def get_index_path(dir):
	'''Get the index page of a directory and return it as .html:
(_always_ return the file + the path !)'''
	
	index_page_md=''
	for file in os.listdir(os.path.join(config.CONTENT_DIR, dir)):
		if 'index' in file:
			# using only one type of subcontent by now !
			# --> corrected using multiple types again
			for type in config.SUBCONTENT_TYPES:
				if not type in file:
					index_page_md=file
	# get the index page
	#index_page_md=get_index_page(top_level_dir)
	# if no index page is found link the directory for now
	#  --> link the listing page, listing pages will always
	#       be named listing.html
	if index_page_md == '':
		index_path=os.path.join(dir, 'listing.html')
	# rename .markdown to .html
	else:
		index_page=index_page_md.split('.')[0]+'.html'
		index_path=os.path.join(dir, index_page)
	# return
	return index_path
	
