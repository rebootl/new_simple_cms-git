'''Module of new_simple_cms

Similar to plugins, markdown* math is handled here.

*In fact this is a pandoc extension using tex math.

Doing this separately cause it offers more possibilities
than the built-in pandoc math processing!

Using latex and dvipng.'''
# Enhancements:
# - Set a maximum line length/width.
#   --> probably set \linewidth
#
# - Make it possible to use any tex code, not only formulas.
#   --> the problem is using $$ there's no way to distinguish between them
#   ==> evtl. $$$ could then be used...
#
# - Print to stdout instead of writing a tmpfile
#   --> use \typeout{\the\mydepth}} !!!
#   ==> but regarding all the output of pdftex to stdout it's prob.
#       best to simply write to a tmpfile as is

# Imports
# python
import os
import re
import tempfile
import subprocess

# global config variables
from config import *

# Settings
# subdirectory name for images
IMG_DIR = 'img-m'

# latex template for math formulas
# (I found this latex code on: mactextoolbox.sourceforge.net/articles/baseline.html)
# Using the commented (%) commands, the size is generated from within latex,
# then it's not necessary to use -T tight in dvipng. However I found this to be
# a bit slower, therefor I'm not using it.) - removed
LATEX_TEMPL = r'''\documentclass[12pt]{{article}}
\usepackage{{amsmath}}
\pagestyle{{empty}}

\newsavebox{{\mybox}}

\newlength{{\mydepth}}

\begin{{lrbox}}{{\mybox}}
$\displaystyle
{formula}
$
\end{{lrbox}}

\settodepth{{\mydepth}}{{\usebox{{\mybox}}}}

\newwrite\foo
\immediate\openout\foo=\jobname.depth
	\immediate\write\foo{{\the\mydepth}}
\closeout\foo

\begin{{document}}
\usebox{{\mybox}}
\end{{document}}

'''

# dvipng options
# resolution in dpi, influences the size
RES_DPI = '145'
# background color
COL_BG = 'Transparent'
# foreground color
COL_FG = 'rgb 0.611765 0.867188 0.867188'

# html tag
IMG_TAG = '<img class="texmath-img" style="vertical-align:{yoff}px;" src="{img_href}" alt="{img_alt}" title="{img_title}" />'


# Functions

def check_math(page_body):
	'''Quick check if there's math content on a page.
Returning True or False.

(If there's math content we'll have to scan a second time.
But if there's none we're faster. Could be done otherwise though.)'''
	# the regex
	# should match $$
	re_math = re.compile('\${2}')
	found = re_math.search(page_body)
	
	if found:
		return True
	else:
		return False
	

def process_formulas(subdir, texmath_formulas):
	'''Process texmath formulas and return HTML code that replaces them.'''
	# set/create the _final_ output directory
	outdir_sub_full = os.path.join(PUBLISH_DIR, subdir, IMG_DIR)
	
	if not os.path.isdir(outdir_sub_full):
		os.makedirs(outdir_sub_full)
	
	# create a temporary working dir
	tmp_wd_ob = tempfile.TemporaryDirectory()
	tmp_wd = tmp_wd_ob.name
	
	#if not os.path.isdir(WORK_DIR):
	#	os.mkdirs(WORK_DIR)
	html_formulas = []
	
	for num, tm_formula in enumerate(texmath_formulas):
		# remove leading and trailing dollars
		tm_form_s = tm_formula.strip("$$")
		
		# insert the formula in the latex template
		latex_form = LATEX_TEMPL.format(formula=tm_form_s)
		
		# write out tex input file to a file in the temporary directory
		mform_name = 'mform_'+str(num)
		texfile_path = os.path.join(tmp_wd, mform_name+'.tex')
		with open(texfile_path, 'w') as texfile:
			texfile.write(latex_form)
		
		# process through latex, gives a dvi
		args = ['latex', '-output-directory', tmp_wd, texfile_path]
		# (catch stdout cause it's annoing blabber (!),
		# errors should still be printed out)
		proc = subprocess.Popen(args, stdout=subprocess.PIPE)
		out_std, out_err = proc.communicate()
		
		#subprocess.call(args)
		
		
		# readout depth file
		depth_file = os.path.join(tmp_wd, mform_name+'.depth')
		with open(depth_file, 'r') as df:
			depth_texpt_str = df.readline()
			depth_texpt = float(depth_texpt_str.strip().rstrip('pt'))
		# (debug-print)
		print("depth texpt: ", depth_texpt)
		
		# convert depth pt to px
		yoff_px = round( depth_texpt * int(RES_DPI) / 72 )
		
		
		# process through dvipng, gives a png, finally
		dvifile_path = os.path.join(tmp_wd, mform_name+'.dvi')
		img_name = mform_name+'.png'
		img_out_path = os.path.join(outdir_sub_full, mform_name+'.png')
		args = ['dvipng', '-T', 'tight', '-D', RES_DPI, '--depth', '-bg', COL_BG, '-fg', COL_FG, '-o', img_out_path, dvifile_path]
		proc = subprocess.Popen(args, stdout=subprocess.PIPE)
		out_std, out_err = proc.communicate()
		
		#subprocess.call(args)
		
		# create the html tag
		img_href = os.path.join(IMG_DIR, img_name)
		img_html = IMG_TAG.format(img_href=img_href, img_alt=tm_form_s, img_title=tm_form_s, yoff=-yoff_px)
		
		html_formulas.append(img_html)
		
	
	# --> evtl. cleanup the temp dir here ==> not necessary
	
	return html_formulas
	

def math_handler(subdir, page_body):
	'''Handling markdown math content.'''
	# the regex
	# should math $$some_tex_formula$$
	re_math = re.compile('\${2}.+?\${2}')
	
	# find and substitute it
	# --> it's not even necessary to substitute them,
	# they can be replaced directly afterwards
	texmath_formulas = re_math.findall(page_body)
	
	# process the formulas
	html_formulas = process_formulas(subdir, texmath_formulas)
	
	# substitute formulas
	for formula in html_formulas:
		page_body = re_math.sub(formula, page_body, 1)
	
	return page_body
	
