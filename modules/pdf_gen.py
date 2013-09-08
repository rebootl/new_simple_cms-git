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
		# (debug-print)
		#print("plugin blocks pdf: ", plugin_blocks_pdf)
		page_body = back_substitute(page_body_subst, plugin_blocks_pdf)
	else:
		page_body = page_body_subst
	
	# create pandoc options for title block values
	opts = []
	for index, tb_value in enumerate(title_block_vals):
		opts.append('--variable='+REGULAR_TB_LINES[index]+':'+tb_value)
	
	# create a temporary working directory for pandoc,
	# to avoid cluttering the cms root
	# (debug)
	#tmp_wd_obj = tempfile.TemporaryDirectory()
	#tmp_wd = tmp_wd_obj.name
	# (debug alternative)
	#tmp_wd = os.path.join(outdir, 'tmp')
	#if not os.path.isdir(tmp_wd):
	#	os.makedirs(tmp_wd)	
	
	# set working directory to current subdir
	cwd = os.getcwd()
	tmp_wd = outdir
	os.chdir(tmp_wd)
	
	#tmp_pdf = os.path.join(tmp_wd, filename_pdf)
	
	# (debug-print)
	print("page body pdf: ", page_body)
	
	# create a temporary md file
	tmp_filename_md = 'gen-pdf-tmp-xxx555.md'
	with open(tmp_filename_md, 'w') as tf:
		tf.write(page_body)
	
	outfile = os.path.join(outdir, filename_pdf)
	
	# call pandoc
	pandoc_command = ['pandoc', tmp_filename_md, '-o', outfile]
	args = pandoc_command+opts
	
	#proc = subprocess.Popen(args, stdin=subprocess.PIPE)
	#input = page_body.encode()
	#
	#stdout, stderr = proc.communicate(input=input)
	subprocess.call(args)
	
	os.chdir(cwd)
	
	# back copy the resulting pdf
	#shutil.copy(tmp_pdf, outdir)
	
	
