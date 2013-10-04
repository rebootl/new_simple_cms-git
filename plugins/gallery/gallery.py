#!/usr/bin/python
'''plugin for new_simple_cms

Insert an image gallery.

Syntax:

[[ GALLERY ][ directory ]]

Where directory should be a directory containing the images.
(If you don't want the directory to appear on the website it should be outside
of content. 
If relative it will be assumed to be in the script directory!)

Images will be resized, thumbnailed and copied into the current public subdir.
(Checking for existing files to speed it up.)

Gallery functionality on the website is controlled by Javascript and CSS.

Using imagemagick's convert.
'''
# This file is part of new_simple_cms
#--------------------------------------------------------------------------------
#
# Copyright 2013 Cem Aydin
#
#--------------------------------------------------------------------------------
# See new_simple_cms.py for more information.

# Imports
#
# python
import os
import subprocess

# global config variables
import config

# common functions
from modules.common import pandoc_pipe


# Plugin settings
# image definitions for website
MAIN_IMAGE_PREFIX="med-"
MAIN_IMAGE_WIDTH="450"
THUMB_IMAGE_PREFIX="thumb-"
THUMB_IMAGE_WIDTH="100"
# image definitions for PDF output
PDF_IMAGE_PREFIX="small-"
PDF_IMAGE_WIDTH="200"


GALLERY_TEMPLATE="plugins/gallery/gallery.html"

# gallery prefix
# (needed for div id that has to be a letter, no digit, blergh)
GALLERY_PREFIX="gal-"


# Functions

def convert_image(infile, width, outfile):
	## Convert an image using imagemagick's convert.	
	convert_command=['convert', '-scale', width, infile, outfile]
	args=convert_command
	
	proc=subprocess.Popen(args)
	


def gallery(subdir, plugin_in):
	gallery_dir=plugin_in
	gallery_name = GALLERY_PREFIX+os.path.basename(gallery_dir)
	
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
	if config.PRODUCE_PDF:
		# returning raw content + remark
		#pdf_md = "[[ GALLERY ] [ "+plugin_in+" ]  \n(Gallery plugin, PDF output not yet supported.)\n"
		# (debug-print)
		#print("pdf md: ", pdf_md)
		
		# inserting images
		# (sort list)
		image_list.sort()
		
		# (MD)
		md_text = "Images  \n"
		
		# (adding an MD image reference for every image)
		for image in image_list:
			
			# (make images)
			image_in_path = os.path.join(gallery_dir, image)
			pdf_image_name = PDF_IMAGE_PREFIX+image
			pdf_image_out_path = os.path.join(images_out_dir, pdf_image_name)
			if not os.path.isfile(pdf_image_out_path):
				convert_image(image_in_path, PDF_IMAGE_WIDTH, pdf_image_out_path)
			
			# (we need the absolute path for the PDF production)
			cwd = os.getcwd()
			images_out_dir_abs = os.path.join(cwd, images_out_dir)
			
			img_name = PDF_IMAGE_PREFIX+image
			
			img_src = os.path.join(images_out_dir_abs, img_name)
			img_alt = ''
			
			md_ref = "![ {alt} ]({src})\n".format(alt=img_alt, src=img_src)
			md_text = md_text+md_ref
			
		pdf_md = md_text
		
	else:
		pdf_md = ""
	
	return gallery_html, pdf_md
	
