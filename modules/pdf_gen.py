'''Module of new_simple_cms

Generate a PDF from input stream.

Atm PDF's are created in the respective content subdirectory.
They are then copied to the publish subdirectory amongst the other
remaining files.
To remove them completely they have to be deleted on both locations.
(This is suboptimal and may lead to confusion but it's needed for the 
inserted images.) --> improve

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
	
	# working directory
	# needs to be the CONTENT_DIR to include images atm.,
	# (--> could evtl. be improved)
	# 
	# the directory is cleaned up and the resulting PDF 
	# is _moved_ to PUBLISH_DIR below,
	wd = os.path.join(config.CONTENT_DIR, subdir)
	
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
	
	# (debug-print)
	#print("page body (for pdf):", page_body)
	
	# set working directory to the respective content subdir
	cwd = os.getcwd()
	os.chdir(wd)
	
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
	
	# move the pdf to the publish directory
	inpath = os.path.join(wd, filename_pdf)
	outdir = os.path.join(config.PUBLISH_DIR, subdir)
	
	# (using copy + remove since shutil.move doesn't overwrite)
	shutil.copy(inpath, outdir)
	os.remove(inpath)
