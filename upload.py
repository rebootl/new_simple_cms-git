#!/usr/bin/python
'''Simple FTP upload script for new_simple_cms

- Shall be able to upload single files, directories and recursive directories.'''

# Imports
# python modules
import os
import argparse

from ftplib import FTP
from ftplib import error_perm

# global config variables
import config

# modules
from modules.common import get_dirs


# Globals
# import FTP account information
from upload_account import FTP_SERVER_URL, FTP_USER, FTP_PASS

# make an FTP instance
# (--> could be made a local variable (?))
FTP_INST=FTP(FTP_SERVER_URL)


# Functions
# connect, disconnect
def connect():
	'''Login to FTP server.'''
	FTP_INST.login(FTP_USER, FTP_PASS)
	# --> check if login successful ?
	# ...
	

def disconnect():
	'''Logout from FTP server.'''
	FTP_INST.quit()
	

def upload(client_dirlist, subdir):
	'''Upload.
Making one upload function using a filelist.'''
	
	# check if directory exists on server
	try:
		FTP_INST.cwd(subdir)
	except error_perm:
		print("Path does not exist on FTP server, create it first by updating upper levels.")
		print("Path: ", subdir)
		print("Returning...")
		return False
	
	# retrieve the current directory content from server
	server_dirlist=FTP_INST.nlst()
	
	# upload the files / create directories
	for item in client_dirlist:
		item_filepath=os.path.join(config.PUBLISH_DIR, subdir, item)
		# files
		if os.path.isfile(item_filepath):
			print("Uploading:", item_filepath)
			file=open(item_filepath, 'rb')
			FTP_INST.storbinary('STOR {}'.format(item), file)
			file.close()
		
		# directory
		elif os.path.isdir(item_filepath):
			# check if it already exists
			if item not in server_dirlist:
				print("Create directory:", item_filepath)
				FTP_INST.mkd(item)
		
		else: 
			print("Filetype could not be determined for file: ", item_filepath)
	
	FTP_INST.cwd('/')
	
	return True
	

def upload_file(filepath):
	# get filename and subdir
	file=os.path.basename(filepath)
	subdir=os.path.dirname(filepath)
	
	real_filepath=os.path.join(config.PUBLISH_DIR, subdir, file)
	
	# check and process
	if os.path.isfile(real_filepath):
		# create dirlist
		dirlist=[file]
		# upload
		connect()
		return_state=upload(dirlist, subdir)
		disconnect()
	else:
		print("File not found: {} in {} Returning...".format(file, subdir))
		return_state=False
	
	return return_state
	

def upload_dir(subdir):
	# check subdir
	subdir_real=os.path.join(config.PUBLISH_DIR, subdir)
	if os.path.isdir(subdir_real):
		# get dirlist
		dirlist=os.listdir(subdir_real)
		# upload
		connect()
		return_state=upload(dirlist, subdir)
		disconnect()
	else:
		print("Directory not found: {} Returning...".format(subdir))
		return_state=False
	
	return return_state


def upload_recursive(subdir):
	# check subdir
	subdir_real=os.path.join(config.PUBLISH_DIR, subdir)
	if not os.path.isdir(subdir_real):
		print("Directory not found: {} Returning...".format(subdir))
		return False
	
	# get subdirs
	subdirs=get_dirs(subdir)
	
	connect()
	return_state_list=[]
	for subdir in subdirs:
		# get dirlist
		real_subdir=os.path.join(config.PUBLISH_DIR, subdir)
		dirlist=os.listdir(real_subdir)
		# upload
		return_state_curr=upload(dirlist, subdir)
		return_state_list.append(return_state_curr)
	
	disconnect()
	if False in return_state_list:
		return_state=False
	else:
		return_state=True
	return return_state
	


def main():
	# Make argument options handling nice.
	# (similar to new_simple_cms)
	parser=argparse.ArgumentParser(description='Upload files/directories to FTP server.')
	
	# positional arg
	parser.add_argument('PATH', help="file or directory to upload, by default PATH is supposed to be a directory, subdirs are created but not further processed (PUBLISH_DIR, from config.py, is automatically prepended)")
	
	# optional args
	group=parser.add_mutually_exclusive_group()
	group.add_argument('-f', '--file', help="only update a single file", action="store_true")
	group.add_argument('-r', '--recursive', help='recursive, upload from given directory on (simply use . for everything)', action='store_true')
	
	# parse args
	args=parser.parse_args()
	
	filepath=args.PATH
	# -f (file)
	if args.file:
		return_state=upload_file(filepath)
	# -r (recursive)
	elif args.recursive:
		return_state=upload_recursive(filepath)
	# default (directory)
	else:
		#filepath_real=os.path.join(PUBLISH_DIR, filepath)
		#if os.path.isfile(filepath_real):
		#	return_state=upload_page(filepath)
		#elif os.path.isdir(filepath_real):
		return_state=upload_dir(filepath)
		#else:
		#	print("File or directory not found: %s Leaving..." % filepath)
		#	sys.exit()
	
	if return_state:
		print("Success!")
	else:
		print("Something went wrong...")
	


if __name__ == '__main__':
	main()

