'''Module of new_simple_cms

Support to process Metapost files.

Metapost files are processed separately and figures are created.

References to the figures are set in the markdown file using the metapost plugin.

Only one .mp file is allowed per directory.
Containing figures as follows:
beginfig(n);
...
endfig;

Using metapost and Imagemagick's convert.'''
# see workflow below
#
# Imports
# python
import os
import tempfile
import subprocess
import re

# global config variables
from config import *

# Settings
# metapost file extension
MP_EXT = ".mp"

# resolution
FIG_RES_DPI = "205"

# image (png) foreground color for HTML output
# (metapost color syntax)
FG_COL_HTML_IMG = "(0.6,0.8,0.8)"

# width
#FIG_WIDTH = "450"

# metapost template
MP_TEMPL = r'''prologues := 3;
%outputtemplate:="%j-%c.svg";
outputtemplate:="%j-%c.svg";
outputformat := "svg";

%drawoptions(withcolor (0.6,0.8,0.8));

verbatimtex
%&latex
\documentclass{{article}}
\begin{{document}}
etex

{mp_figs}

end;'''


# Functions
#
# workflow is as follows
# 
# 1) find the .mp file
# 2) read it
# 3) insert it in a latex template
#    configured to output as svg
#
# 4) call mpost, creates svg
#
# 5) call convert w/ following options e.g.:
#    -density 150 -geometry 450 -background transparent fig-1.svg fig-1.png
#

def check_mp(subdir):
	'''Quick check if there's an .mp file.

Returning the Metapost file if found or False.'''
	dir = os.path.join(CONTENT_DIR, subdir)
	dir_content = os.listdir(dir)
	
	for file in dir_content:
		if file.endswith(MP_EXT):
			return file
	
	return False


def handle_metapost(subdir):
	'''Processing Metapost content directory wise.'''
	
	mp_file = check_mp(subdir)
	
	if not mp_file:
		return
	
	# set out dir
	# (setting this to content, images are needed there for PDF creation,
	#  together with the other arbitrary files, they will be copied by the 
	#  cms to the publish dir)
	outdir = os.path.join(CONTENT_DIR, subdir)
	
	# read the mp file
	mp_filepath = os.path.join(CONTENT_DIR, subdir, mp_file)
	
	with open(mp_filepath, 'r') as f:
		mp = f.read()
	
	process_metapost(outdir, mp_file, mp)
	

def def_fig_color(mp):
	'''Find the beginfig(n); tags and add the color specification after them.'''
	re_beginfig = re.compile(r'beginfig\([0-9]*\);')
	beginfigs = re_beginfig.findall(mp)
	
	color_str = '\ndrawoptions(withcolor '+FG_COL_HTML_IMG+');\n\n'
	
	print("beginfigs: ", beginfigs)
	
	mp_col = mp
	for beginfig in beginfigs:
		replacer = beginfig+color_str
		
		mp_col = mp_col.replace(beginfig, replacer)
	
	return mp_col
	

def process_metapost(outdir, filename, mp):
	'''Processing routine for metapost.

(Ded. to be also used by the metapost plugin.)'''

	# create a temporary working directory
	tmp_wd_obj = tempfile.TemporaryDirectory()
	tmp_wd = tmp_wd_obj.name
	#tmp_wd = os.path.join(outdir, 'tmp')
	#os.makedirs(tmp_wd)
	
	# (debug-print)
	#print("mp: ", mp)
	#print("MP_TEMPL: ", MP_TEMPL)
	
	# add the image fg color (for HTML output)
	mp_col = def_fig_color(mp)
	
	# insert the figs into the template
	mp_full = MP_TEMPL.format(mp_figs=mp_col)
	
	# (debug-print)
	print("mp full: ", mp_full)
	
	# write a temporary .mp file
	tmpfile_mp_path = os.path.join(tmp_wd, filename)
	#tmpfile_mp_path = os.path.join(outdir, mp_file)
	with open(tmpfile_mp_path, 'w') as f:
		f.write(mp_full)
	
	wd = os.getcwd()
	os.chdir(tmp_wd)
	
	# call metapost
	args = ['mpost', '-tex=latex', '-debug', filename]
	#proc = subprocess.Popen(args, stdout=subprocess.PIPE)
	#out_std, out_err = proc.communicate()
	
	subprocess.call(args)
	
	os.chdir(wd)
	
	# get the svg files
	svg_files = []
	tmpfiles = os.listdir(tmp_wd)
	# (debug-print)
	print("tmp wd: ", tmp_wd)
	print("tmpfiles: ", tmpfiles)
	
	for file in tmpfiles:
		if file.endswith('.svg'):
			svg_files.append(file)
	
	# (debug-print)
	print("svg files: ", svg_files)
	
	# convert to png's
	for svg_file in svg_files:
		
		inpath = os.path.join(tmp_wd, svg_file)
		outpath = os.path.join(outdir, svg_file.split('.')[0]+'.png')
		
		# call convert
		args = ['convert', '-density', FIG_RES_DPI, '-background', 'transparent', inpath, outpath ]
		subprocess.call(args)
		
	
