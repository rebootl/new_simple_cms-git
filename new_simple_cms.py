#!/usr/bin/python
'''a little static website generator, created for my personal use

Using pandoc. (Slightly extended markdown.)

Desired features:
 - An input directory tree reflects the website structure.
 - Content can be created by posts for _every_ page ! (Except Directory listing pages.)
 - Enhanced/expandable use of templates:
   I.e. minor templates for posts and navigation can be used.
   (Realized by pre-generating the minor content and inserting it
    afterwards in the major template, using pandoc.)
    --> Not using pandoc for this anymore. It's nonsense and it's __way__
        faster by simply generating the HTML in the code. I didn't wanted to 
        do this before, but now I see no reason not to do it anymore.
        (I looked into several templating systems but could not find
         a suitable simple system for Python 3.)
 - Directory listing.
 - Automatic menu (Navigation) generation.
 - If possible, generate readable (x)html.
 - Generate valid XHTML. (Set the appropriate doctype, content/tag dependend.)
 - A simple plugin system !
 - A gallery page feature... maybe. --> Implemented as plugin.
 - No CSS processing !
 - No tempfiles are written to disk.
   (--> Using tempfile python module for latex etc. processing.)

New features:
 - A frontend for local use ! (--> in development)
 - Complete CLI w/ arguments and checks !
 - Math processing using latex and dvipng.

Plugins:
 - Insert file
 - Gallery
 - Tree
 - Metapost

Next:
 - Production of high-quality PDF files for every page using Pandoc ! (incl. plugins, excl. listing pages, atm)

Inspired by Jekyll and Xac.
'''
# License and Copyright:
#--------------------------------------------------------------------------------
#
# Copyright 2013 Cem Aydin
#
#--------------------------------------------------------------------------------
#
# Regarding the code I used almost nothing from Xac, however I mention it's
# copyright here.
# Basically I learned about Pandoc and Markdown from it. The directory structure
# is similar, as it is in Jekyll.
#
# Xac copyright:
# Copyright (C) 2012  Xyne
#
#--------------------------------------------------------------------------------
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# (version 2) as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#--------------------------------------------------------------------------------
# Author: Cem Aydin
# E-Mail: cem.aydin gmx.ch

# Imports
# python modules
import os
import sys
import argparse

# global config variables
# (Importing * here, the global config variables are identified by capital letters.)
# --> better use import config
# (global variables can be changed using this)
#from config import *
import config

# modules
from modules.processing import process_dir, preprocess_page_group, prepare_final, process_page, handle_math
from modules.common import pandoc_final, pandoc_pipe_from_file, get_dirs, copy_remaining_content, copy_listing_content, extract_title_block, pandoc_pipe, write_out, scan_doctype
from modules.main_menu import generate_main_menu
from modules.section_menu import generate_section_menu
from modules.listing import get_listing_page, gen_listing_table_entries, gen_listing_path_items, prepare_final_listing
from modules.plugin_handler import back_substitute
#from modules.metapost_handler import handle_metapost
from modules.pdf_gen import generate_pdf


# main flow control plan
#
# /* must be rewritten */
#


# Functions

def make_regular_pages(pages_struct, subdir):
	'''Main function to create regular pages.'''
	for page_group in pages_struct:
		# (info-prints)
		print("Page: ", os.path.join(subdir, page_group[0]))
		#print('Preprocessing:', page_group[0])
		#for subcontent in page_group[1:]:
		#	print(' Subcontent:', subcontent)
		#print('Page group:', page_group)
		
		# Preprocess page
		main_page_body_subst, plugin_blocks, plugin_blocks_pdf, main_page_tb_vals=preprocess_page_group(subdir, page_group)
		
		# (scan doctype)
		body_doctype=scan_doctype(main_page_body_subst)
		
		# Preprocess math content
		if config.PROCESS_MATH:
			main_page_body_subst_m = handle_math(subdir, page_group[0], main_page_body_subst)
		else:
			main_page_body_subst_m = main_page_body_subst
		
		# Generate the menus
		#
		# main menu
		# (info-prints)
		#print('Generate main menu.')
		#print('Subdir:', subdir, 'Page group [0]:', page_group[0])
		main_menu=generate_main_menu(subdir, page_group[0])
		
		# section menu
		# (info-prints)
		#print('Generate section menu.')
		section_menu_list=generate_section_menu(subdir, page_group[0])
		
		# Finalize this page
		# prepare for final output
		final_opts, out_filepath=prepare_final(subdir, page_group, main_page_tb_vals, main_menu, section_menu_list, body_doctype)
		
		# (debug-print)
		#print("main page body subst: ", main_page_body_subst)
		
		# final pandoc processing
		final_html_subst=pandoc_pipe(main_page_body_subst_m, final_opts)
		
		# (debug-print)
		#print("final html subst: ", final_html_subst)
		
		# back substitute
		if plugin_blocks != []:
			final_html=back_substitute(final_html_subst, plugin_blocks)
		else:
			final_html=final_html_subst
		
		# write out
		# (info-print)
		print('Writing:', out_filepath)
		write_out(final_html, out_filepath)
		
		# PDF production
		if config.PRODUCE_PDF:
			# (info-print)
			print("Produce a PDF.")
			# (plugins must provide blocks for pdf's)
			generate_pdf(subdir, page_group[0], main_page_body_subst, plugin_blocks_pdf, main_page_tb_vals)
	

def make_listing_page(subdir):
	'''Main function to create a directory listing page.'''
	#
	# look if there is a -listing- page
	# preprocess that page
	listing_page_md=get_listing_page(subdir)
	
	if listing_page_md != '':
		infile=os.path.join(config.CONTENT_DIR, subdir, listing_page_md)
		opts=[]
		
		# adding title block extraction here
		# (using them only for the final output below, atm)
		listing_page_body, title_block_vals=extract_title_block(infile, config.REGULAR_TB_LINES)
		
		listing_body_doctype=scan_doctype(listing_page_body)
	
	else:
		title_block_vals=[]
		listing_page_body=''
		listing_body_doctype='strict'
	
	# (debug-print)
	#print('Listing Page Body:', listing_page_body)
	
	# make the content listing
	listing_table_entries_str=gen_listing_table_entries(subdir, listing_page_md)
	
	# (debug-info)
	#print('Listing_table:', listing_table)
	
	# get/set the parent dir (for the path line)
	# this should go in a separate funtion, but it doesn't work
	#getset_parent_dir(subdir)
	# --> now using import config, this could probably be improved ...
	if config.LISTING_PARENT_DIR == '' :
		config.LISTING_PARENT_DIR=subdir
	elif config.LISTING_PARENT_DIR in subdir:
		pass
	else: config.LISTING_PARENT_DIR=subdir
	# (debug-info)
	#print('Subdir:', subdir)
	#print('Parent dir:', LISTING_PARENT_DIR)
	parent_dir=config.LISTING_PARENT_DIR
	
	# generate the path line
	listing_path_items=gen_listing_path_items(subdir, parent_dir, listing_page_md)
	
	# generate the main menu
	main_menu=generate_main_menu(subdir, listing_page_md)
	
	# prepare for output
	final_opts, out_filepath=prepare_final_listing(subdir, listing_path_items, listing_table_entries_str, main_menu, title_block_vals, listing_body_doctype)
	
	# final pandoc processing
	final_html=pandoc_pipe(listing_page_body, final_opts)
	
	# write out
	write_out(final_html, out_filepath)
	

# Refreshing options
# - page: [[ main-page, subcont-1, subcont-2, .. ]]
# - subdir: [[ main-page-1, subcont-1, .. ], [ main-page-2, subcont-1, .. ], .. ]
# - subdirs (recursive): for subdir in subdirs " "
# - all: " "
#
# Make clean functions for these cases:
# (Callable from CLI (main, below) and also from CGI!)
#
def refresh_page(page, subdir):
	'''Control function for one page.

- Initiate refresh/creation.
- Copy the remaining folder content.'''
	# --> to get active class subdir needs to be set to '.'
	if subdir == '':
		subdir = '.'
	
	# (info-print)
	print("Processing: ", subdir, page)
	
	pages_struct=process_page(page, subdir)
	
	if pages_struct != []:
		make_regular_pages(pages_struct, subdir)
	else:
		make_listing_page(subdir)
	

def refresh_subdir(subdir):
	'''Control function for one subdirectory.

- Initiate refresh/creation.
- Copy the remaining folder content.'''
	pages_struct=process_dir(subdir)
	
	# (info-print)
	print("Processing: ", subdir)
	
	if pages_struct != []:
		make_regular_pages(pages_struct, subdir)
		copy_remaining_content(subdir)
	else:
		make_listing_page(subdir)
		copy_listing_content(subdir)
	

def refresh_subdirs_recursive(refresh_dir):
	'''Control function acting recursively from given directory on.

- Initiate refresh/creation.
- Copy the remaining folder content.'''
	subdirs=get_dirs(refresh_dir)
	
	# process dirs
	for subdir in subdirs:
		print('Processing: ', subdir)
		# (call process_dir)
		pages_struct=process_dir(subdir)
		
		# if no index page is found a directory listing will be created
		if pages_struct != []:
			make_regular_pages(pages_struct, subdir)
			copy_remaining_content(subdir)
		else:
			make_listing_page(subdir)
			copy_listing_content(subdir)
	

# Main
def main():
	'''The main function called at commandline invocation.

- Argument parsing and initialising subsequent actions.'''
	# Make a nice argument/options handling !
	# using argparse
	parser=argparse.ArgumentParser(description='Generate website from files/directory structure.', epilog='Using Pandoc and Markdown.')
	
	# add positional argument
	parser.add_argument('PATH', help="PATH frowm where to start refreshing (recursive, simply use . for everything, the full path is created automatically by prepending CONTENT_DIR, from config.py, to PATH)")
	
	# add optional arguments
	# --> leads to problems at importing
	# --> need to find a solution for global controller variables
	# ==> changed import method for global variables, should work now
	parser.add_argument('--pdf', help="produce a PDF file for every page", action="store_true")
	
	# (grouping)
	group=parser.add_mutually_exclusive_group()
	group.add_argument('-f', '--file', help="only refresh a given page specified by PATH", action="store_true")
	group.add_argument('-o', '--only-subdir', help="only refresh a given subdir specified by PATH (not recursive)", action="store_true")
	
	#group.add_argument('-r', '--subdir', help="refresh recursively from the given subdir SUBDIR on, inside CONTENT_DIR")
	
	# parse arguments
	args=parser.parse_args()
	
	filepath=args.PATH
	# --pdf
	if args.pdf:
		# set global config variable
		config.PRODUCE_PDF = True
	
	# -f FILE
	if args.file:
		# check filename
		if '.' not in filepath:
			filepath = filepath+config.MD_EXT
		elif filepath.endswith(config.MD_EXT):
			pass
		elif filepath.endswith(".html"):
			filepath=filepath.split(".")[0]+config.MD_EXT
		else:
			print("Wrong file type extension, should be None, .markdown or .html (.markdown will be used)... Leaving.")
			sys.exit()
			
		# check file
		if not os.path.isfile(os.path.join(config.CONTENT_DIR, filepath)):
			print("File not found... leaving. File:", os.path.join(config.CONTENT_DIR, filepath))
			sys.exit()
		
		pagename=os.path.basename(filepath)
		subdir=os.path.dirname(filepath)
		
		refresh_page(pagename, subdir)
	
	# -o ONLY_SUBDIR
	elif args.only_subdir:
		# check subdir
		if not os.path.isdir(os.path.join(config.CONTENT_DIR, filepath)):
			print("Directory not found... Leaving.")
			sys.exit()
		
		refresh_subdir(filepath)
	
	# default (recursive)
	else:
		# check subdir
		if not os.path.isdir(os.path.join(config.CONTENT_DIR, filepath)):
			print("Directory not found... Leaving.")
			sys.exit()
		
		refresh_subdirs_recursive(filepath)
	
	# all (recursive)
	# (not used anymore (?))
	#else:
	#	refresh_subdirs_recursive('.')
	


# make it, respectively its functions importable w/o executing
# (used for the CGI)
if __name__ == '__main__':
	main()
