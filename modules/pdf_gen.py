'''Modules of new_simple_cms

Generate a PDF from input stream.

Using Pandoc.'''

# Imports
# python
import os
import tempfile
import subprocess
import shutil

# global config variables
from config import *

# common
from modules.plugin_handler import back_substitute


# Funtions

def generate_pdf(subdir, filename_md, page_body_subst, plugin_blocks_pdf, title_block_vals):
	'''Main PDF generator function.'''
	
	# final output directory
	# (setting this into CONTENT_DIR atm,
	#  PDF's will be copied with the rest)
	outdir = os.path.join(CONTENT_DIR, subdir)
	
	filename_pdf = filename_md.split('.')[0]+'.pdf'
	
	# back substitute the plugin blocks into the page body
	if plugin_blocks_pdf != []:
		page_body = back_substitute(page_body_subst, plugin_block_pdf)
	else:
		page_body = page_body_subst
	
	# create pandoc options for title block values
	opts = []
	for index, tb_value in enumerate(title_block_vals):
		opts.append('--variable='+REGULAR_TB_LINES[index]+':'+tb_value)
	
	# create a temporary working directory for pandoc,
	# to avoid cluttering the cms root
	tmp_wd_obj = tempfile.TemporaryDirectory()
	tmp_wd = tmp_wd_obj.name
	
	cwd = os.getcwd()
	os.chdir(tmp_wd)
	
	tmp_pdf = os.path.join(tmp_wd, filename_pdf)
	
	# call pandoc
	pandoc_command = ['pandoc', '-o', tmp_pdf]
	args = pandoc_command+opts
	
	proc = subprocess.Popen(args, stdin=subprocess.PIPE)
	input = page_body.encode()
	
	stdout, stderr = proc.communicate(input=input)
	
	os.chdir(cwd)
	
	# back copy the resulting pdf
	shutil.copy(tmp_pdf, outdir)
	
	
