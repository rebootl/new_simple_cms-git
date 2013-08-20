#!/usr/bin/python
#
# Simple webserver for testing purposes.
#
# Using the python module http.server.
#
# Trying to enable CGI...
#
##

## Import modules:
import os
from http.server import HTTPServer, CGIHTTPRequestHandler

## Import config:
from config import *

## Change WD:
os.chdir(PUBLISH_DIR)

## Server:
serve=HTTPServer(('', 8000), CGIHTTPRequestHandler)
serve.serve_forever()
