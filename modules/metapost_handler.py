'''Module of new_simple_cms

Support to process Metapost files.

Metapost files are processed separately and images (PNG) are created.

Links to the images have to be set manually in the Markdown files.
(This might be a bit cumersome but it's fully compliant with latex/pdf
creation.)

Only one .mp file is allowed per directory.
Containing figures as follows:
beginfig(n);
...
endfig;

Resulting PNG's are named <metapost-filename>-<n>.png

Using metapost and Imagemagick's convert.'''
# see workflow below
#
# Imports
# python
import os
import tempfile
import subprocess

# global config variables
from config import *

# Settings
# metapost file extension
MP_EXT = ".mp"

# resolution
FIG_RES_DPI = "250"

# width
FIG_WIDTH = "450"

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

{0}

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
	'''Quick check if there's an .mp file.'''
	dir = os.path.join(CONTENT_DIR, subdir)
	dir_content = os.listdir(dir)
	
	for file in dir_content:
		if file.endswith(MP_EXT):
			return file
	
	return False


def process_metapost(subdir):
	'''Processing Metapost content directory wise.

Returning the Metapost file if found or False.'''
	
	mp_file = check_mp(subdir)
	
	if not mp_file:
		return
	
	# set out dir
	# (setting this to content, images are needed there for PDF creation,
	#  together with the other arbitrary files, they will be copied by the 
	#  cms to the publish dir)
	outdir = os.path.join(CONTENT_DIR, subdir)
	
	# create a temporary working directory
	#tmp_wd_obj = tempfile.TemporaryDirectory()
	#tmp_wd = tmp_wd_obj.name
	tmp_wd = os.path.join(outdir, 'tmp')
	os.makedirs(tmp_wd)
	
	# read file
	mp_filepath = os.path.join(CONTENT_DIR, subdir, mp_file)
	
	with open(mp_filepath, 'r') as f:
		mp = f.read()
	
	# (debug-print)
	print("mp: ", mp)
	print("MP_TEMPL: ", MP_TEMPL)
	
	# insert the figs into the template
	mp_full = MP_TEMPL.format(mp)
	
	# (debug-print)
	#print("mp full: ", mp_full)
	
	# write a temporary .mp file
	tmpfile_mp_path = os.path.join(tmp_wd, mp_file)
	#tmpfile_mp_path = os.path.join(outdir, mp_file)
	with open(tmpfile_mp_path, 'w') as f:
		f.write(mp_full)
	
	wd = os.getcwd()
	os.chdir(tmp_wd)
	
	# call metapost
	args = ['mpost', '-tex=latex', '-debug', mp_file]
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
		
	
