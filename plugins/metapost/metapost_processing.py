'''processing functions for Metpost

Used by the metapost plugin.

Using metapost and Imagemagick's convert.
'''
# This file is part of new_simple_cms
#--------------------------------------------------------------------------------
#
# Copyright 2013 Cem Aydin
#
#--------------------------------------------------------------------------------
# See new_simple_cms.py for more information.

# see workflow below
#
# Imports
# python
import os
import tempfile
import subprocess
import re
import shutil

# global config variables
import config

# common
from modules.common import copy_file_abs

# resolution (for HTML output)
# (in dpi)
# influences the resulting size of the PNG
FIG_RES_DPI = "150"

# image (png) foreground color (for HTML output)
# (metapost color syntax)
FG_COL_HTML_IMG = "(0.6,0.8,0.8)"

# metapost template
MP_TEMPL = r'''prologues := 3;
outputtemplate:="%j-%c.eps";
%outputformat := "svg";

verbatimtex
%&latex
\documentclass{{article}}
\begin{{document}}
etex

{mp_figs}

end;'''


# workflow is as follows
# 
# 1) find the .mp file (done by the plugin now)
# 2) read it (done by the plugin now)
# 3) insert it in a latex template
#    configured to output as svg
#
# 4) call mpost, creates svg
#
# 5) call convert w/ following options e.g.:
#    -density 150 -geometry 450 -background transparent fig-1.svg fig-1.png
#

# Functions	

def def_fig_color(mp):
	'''Find the beginfig(n); tags and add the color specification after them.'''
	re_beginfig = re.compile(r'beginfig\([0-9]*\);')
	beginfigs = re_beginfig.findall(mp)
	
	color_str = '\ndrawoptions(withcolor '+FG_COL_HTML_IMG+');\n\n'
	
	# (debug-print)
	#print("beginfigs: ", beginfigs)
	
	mp_col = mp
	for beginfig in beginfigs:
		replacer = beginfig+color_str
		
		mp_col = mp_col.replace(beginfig, replacer)
	
	return mp_col
	

def call_mpost(mp, tmp_wd, filename):
	'''Temporary processing of metapost.'''
	# write a temporary .mp file
	tmpfile_mp_path = os.path.join(tmp_wd, filename)
	
	with open(tmpfile_mp_path, 'w') as f:
		f.write(mp)
	
	wd = os.getcwd()
	os.chdir(tmp_wd)
	
	# call metapost
	# (use -debug if needed)
	args = ['mpost', '-tex=latex', filename]
	proc = subprocess.Popen(args, stdout=subprocess.PIPE)
	out_std, out_err = proc.communicate()
	
	#subprocess.call(args)
	
	os.chdir(wd)
	

def process_metapost(subdir, filename, mp):
	'''Processing routine for metapost.

(Ded. to be also used by the metapost plugin.)'''
	
	# set out dir
	# (setting this to content, for now)
	# (eps files for PDF creation have to be there, see below)
	outdir = os.path.join(config.CONTENT_DIR, subdir)
	
	# create a temporary working directory
	tmp_wd_obj = tempfile.TemporaryDirectory()
	tmp_wd = tmp_wd_obj.name
	# (debug alternative)
	#tmp_wd = os.path.join(outdir, 'tmp')
	#if not os.path.isdir(tmp_wd):
	#   os.makedirs(tmp_wd)
	
	# (debug-print)
	#print("mp: ", mp)
	#print("MP_TEMPL: ", MP_TEMPL)
	
	# insert the figs into the template
	mp_full = MP_TEMPL.format(mp_figs=mp)
	
	# add the image fg color (for HTML output)
	mp_col = def_fig_color(mp_full)
	
	# (debug-print)
	#print("mp full: ", mp_full)
	
	# mpost processing (temporary)
	call_mpost(mp_col, tmp_wd, filename)
	
	# get the eps files
	tmpfiles = os.listdir(tmp_wd)
	
	# (debug-print)
	#print("tmp wd: ", tmp_wd)
	#print("tmpfiles: ", tmpfiles)
	
	eps_files = []
	for file in tmpfiles:
		if file.endswith('.eps'):
			eps_files.append(file)
	
	# (debug-print)
	#print("eps files: ", eps_files)
	
	# convert to png's
	for eps_file in eps_files:
		
		inpath = os.path.join(tmp_wd, eps_file)
		outpath = os.path.join(outdir, eps_file.split('.')[0]+'.png')
		
		# call convert
		args = ['convert', '-density', FIG_RES_DPI, '-background', 'transparent', inpath, outpath ]
		subprocess.call(args)
		
	
	if config.PRODUCE_PDF:
		# produce eps for PDF output
		# (the eps has to be produced again because here we want default
		#  foreground colors)
		call_mpost(mp_full, tmp_wd, filename)
		
		# (debug-print)
		#print("eps files: ", eps_files)
		
		# copy the eps files to the content directory,
		# for later use in PDF creation
		# (the references to the eps files will be created by the plugin)
		for eps_file in eps_files:
			
			inpath = os.path.join(tmp_wd, eps_file)
			outdir = os.path.join(config.CONTENT_DIR, subdir)
			
			# (debug-print)
			#print("inpath: ", inpath)
			#print("outdir: ", outdir)
			# --> have to call copy here cause the tmpdir is destroyed otherwise
			# --> no cp seems not to work on temporary directory (?)
			# --> therefor using shutil.copy below, works well
			#copy_file_abs(inpath, outpath)
			
			shutil.copy(inpath, outdir)
			
	
