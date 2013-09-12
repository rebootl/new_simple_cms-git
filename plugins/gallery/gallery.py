#!/usr/bin/python
'''Plugin for new_simple_cms.

Insert an image gallery.

CDATA syntax:

<![GALLERY[directory]]>

Where _directory_ should be a directory containing the images.
(If you don't want the directory to appear on the website it should be outside of content. 
If relative it will be assumed to be in the script directory!)

Images will be resized, thumbnailed and copied into the current public subdir.
(Checking for existing files to speed it up.)

Gallery functionality on the website is controlled by Javascript and CSS.

Using imagemagick's convert.'''

## Imports:
#
# python
import os
import subprocess

# global config variables
import config

# common functions
from modules.common import pandoc_pipe

## Plugin config variables:
MAIN_IMAGE_PREFIX="small-"
MAIN_IMAGE_WIDTH="450"
THUMB_IMAGE_PREFIX="thumb-"
THUMB_IMAGE_WIDTH="100"

GALLERY_TEMPLATE="plugins/gallery/gallery.html"

def convert_image(infile, width, outfile):
	## Convert an image using imagemagick's convert.	
	convert_command=['convert', '-scale', width, infile, outfile]
	args=convert_command
	
	proc=subprocess.Popen(args)
	


def gallery(subdir, plugin_in):
	gallery_dir=plugin_in
	gallery_name=os.path.basename(gallery_dir)
	
	# check if the directory exists
	if os.path.isdir(plugin_in):
		print("Inserting gallery:", gallery_dir)
		pass
	else:
		dir_not_found_error="GALLERY plugin error: Directory "+gallery_dir+" not found."
		print(dir_not_found_error)
		return dir_not_found_error, dir_not_found_error
	
	## Handle the images:
	# set the out dir
	images_out_dir=os.path.join(config.PUBLISH_DIR, subdir, gallery_name)
	
	# get the images
	filelist=os.listdir(gallery_dir)
	
	image_list=[]
	for file in filelist:
		if file.endswith(".jpg"):
			image_list.append(file)
		elif file.endswith(".png"):
			image_list.append(file)
	
	# make the thumbs and main images
	if not os.path.isdir(images_out_dir):
		os.makedirs(images_out_dir)
	
	thumbs_list=[]
	#main_images_list=[]
	for image in image_list:
		# set the prefix, infile, outfile
		# (make lists for later handling)
		thumb_name=THUMB_IMAGE_PREFIX+image
		thumbs_list.append(thumb_name)
		main_image_name=MAIN_IMAGE_PREFIX+image
		#main_images_list.append(main_image_name)
		
		image_in_path=os.path.join(gallery_dir, image)
		thumb_out_path=os.path.join(images_out_dir, thumb_name)
		main_image_out_path=os.path.join(images_out_dir, main_image_name)
		
		if not os.path.isfile(thumb_out_path):
			convert_image(image_in_path, THUMB_IMAGE_WIDTH, thumb_out_path)
		
		if not os.path.isfile(main_image_out_path):
			convert_image(image_in_path, MAIN_IMAGE_WIDTH, main_image_out_path)
	
	## Make the HTML:
	# make the thumb lines
	# sort and reverse order for pandoc
	thumbs_list.sort()
	thumbs_list.reverse()
	thumb_lines=[]
	for thumb in thumbs_list:
		img_src=os.path.join(gallery_name, thumb)
		# image alt text should be inserted from db (text file) here
		img_alt=''
		# writing html here to speed up things...
		thumb_line='<img src="{}" alt="{}" onclick="change_image(this, parentNode.parentNode.id)" style="width:auto;"/>'.format(img_src, img_alt)
		
		thumb_lines.append(thumb_line)
	
	# make the gallery
	opts=['--template', GALLERY_TEMPLATE]
	
	opts.append('--variable=gallery-name:'+gallery_name)
	
	for line in thumb_lines:
		opts.append('--variable=thumb-img-line:'+line)
	
	gallery_html=pandoc_pipe('', opts)
	
	# output for PDF production
	# (returning raw content + remark, atm)
	if config.PRODUCE_PDF:
		pdf_md = "[[ GALLERY ] [ "+plugin_in+" ]  \n(Gallery plugin, PDF output not yet supported.)\n"
		print("pdf md: ", pdf_md)
	else:
		pdf_md = ""
	
	return gallery_html, pdf_md
	

