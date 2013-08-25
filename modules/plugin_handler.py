'''Module of new_simple_cms

Plugin handling functions.'''

# Imports
#
# python
import re

# global config variables
from config import *

# plugins
from plugins.insert_file.insert_file import insert_file
from plugins.gallery.gallery import gallery
from plugins.tree.tree import tree


# Functions

def plugin_cdata_handler(subdir, cdata_blocks):
	'''Receive the cdata blocks and forward them to the appropriate plugin.'''
	#
	#
	plugin_blocks=[]
	for block in cdata_blocks:
		# extract plugin name and content from cdata block
		#block_split=block.split('[')
		#plugin_name=block_split[1]
		#
		#plugin_rest=''.join(block_split[2:])
		#plugin_rest_split=plugin_rest.split(']')
		#
		#plugin_in=plugin_rest_split[0]
		
		# --> adapting to new selector format
		block_split = block.split(']')
		plugin_name = block_split[0].strip('[[').strip()
		
		plugin_in = block_split[1].strip().strip('[').strip()
		
		
		# here now we forward the blocks to the appropriate plugins
		## Each plugin needs an entry here !
		#plugin_names=
		if plugin_name=='INSERTFILE':
			plugin_out=insert_file(subdir, plugin_in)
			#plugin_out=plugin_content
		
		elif plugin_name=='GALLERY':
			plugin_out=gallery(subdir, plugin_in)
		
		elif plugin_name=='TREE':
			plugin_out=tree(subdir, plugin_in)
		#elif plugin_name=' ... ':
		#	plugin_out=plugins. .. (plugin_content)
		# if no plugin is found return the raw content
		else:
			print("No plugin named:", plugin_name, "found,\n returning raw content.")
			plugin_out=block
		
		plugin_blocks.append(plugin_out)
	
	return plugin_blocks
	

def get_cdata(text):
	'''Get the cdata blocks and replace them by a placeholder.

Return the text and the blocks.'''
	#
	# the regex for cdata
	# should be <![TYPE[DATA]]> --> change to [[ TYPE ] [ DATA ]]
	re_cdata=re.compile(r'\[\[.+?\]\]', re.DOTALL)
	cdata_blocks=re_cdata.findall(text)
	
	text_rep=text
	for block in cdata_blocks:
		text_rep=text_rep.replace(block, PLUGIN_PLACEHOLDER)
	
	# (debug-info)
	#print('Cdata blocks:', cdata_blocks)
	#print('Text rep:', text_rep)
	
	return text_rep, cdata_blocks
	


def back_substitute(text, cdata_blocks):
	'''Back substitution of plugin content.'''
	for block in cdata_blocks:
		# (debug-info)
		#print('Block:', block)
		text=text.replace(PLUGIN_PLACEHOLDER, block, 1)
	
	# (debug-info)
	#print('Text:', text)
	
	return text
	

