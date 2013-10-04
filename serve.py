#!/usr/bin/python
'''simple webserver for new_simple_cms

Using the python module http.server.

CGI enabled.
'''

# Import 
# python modules
import os
from http.server import HTTPServer, CGIHTTPRequestHandler

# config
#from config import *
import config

## Change WD:
os.chdir(config.PUBLISH_DIR)

## Server:
serve=HTTPServer(('', 8000), CGIHTTPRequestHandler)
serve.serve_forever()
