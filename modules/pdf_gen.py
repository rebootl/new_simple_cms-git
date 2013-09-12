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
import config

# common
from modules.plugin_handler import back_substitute


# Funtions

def generate_pdf(subdir, filename_md, page_body_subst, plugin_blocks_pdf, title_block_vals):
	'''Main PDF generator function.'''
	
	# final output directory
	# (setting this into CONTENT_DIR atm,
	#  PDF's will be copied with the rest)
	outdir = os.path.join(config.CONTENT_DIR, subdir)
	
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
		opts.append('--variable='+config.REGULAR_TB_LINES[index]+':'+tb_value)
	
	# create a temporary working directory for pandoc,
	# to avoid cluttering the cms root
	# --> this doesn't work cause pandoc cannot find included images then
	
	# (debug-print)
	#print("page body (for pdf):", page_body)
	
	# --> set working directory to the current subdir
	cwd = os.getcwd()
	
	os.chdir(outdir)
	
	# create a temporary md file
	#tmp_filename_md = 'gen-pdf-tmp-xxx555.md'
	#with open(tmp_filename_md, 'w') as tf:
	#	tf.write(page_body)
	
	# call pandoc
	pandoc_command = ['pandoc', '-o', filename_pdf]
	args = pandoc_command+opts
	
	proc = subprocess.Popen(args, stdin=subprocess.PIPE)
	input = page_body.encode()
	
	stdout, stderr = proc.communicate(input=input)
	#subprocess.call(args)
	
	# cleanup the subdir from temporary files
	files = os.listdir('.')
	
	tmpfiles = []
	for file in files:
		if '-eps-converted-to.pdf' in file:
			tmpfiles.append(file)
	
	for tmpfile in tmpfiles:
		os.remove(tmpfile)
	
	os.chdir(cwd)
