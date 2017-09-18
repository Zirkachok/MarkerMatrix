#!/usr/bin/env python

"""
Visible Marker
Lists requirement markers in documents, and builds a traceability matrix
"""
__author__ = "Julien Beaudaux"
__email__ = "julienbeaudaux@gmail.com"
__version__ = "1.0"
__license__ = "GPL"

import sys, os, time
import argparse
import ntpath

import odfManager
import docxManager

from clint.textui import colored, puts


supportedFormats = ["odt", "docx", "xlsx"]


def is_valid_file(parser, arg):
	if not os.path.exists(arg):
		parser.error("The file %s does not exist!" % arg)
	else:
		if len(arg.split(".")) < 2:
			parser.error("Provided path %s does not lead to a document file!" % arg)
		elif not (arg.split(".")[-1] in supportedFormats):
			parser.error("File format %s not supported!" % arg.split(".")[-1])
		else:
			return arg


def get_file_type(path):
	if not os.path.exists(path):
		return ""
	else:
		if len(path.split(".")) < 2:
			return ""
		elif path.split(".")[-1] in supportedFormats:
			return path.split(".")[-1]
		else:
			return ""


def show_version():
	print colored.blue(__doc__)
	print colored.blue("Version V" +__version__ + " ; License "+__license__+"\n")


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("docfiles", help="input document to test", metavar="FILE", nargs='+', type=lambda x: is_valid_file(parser, x))
	# parser.add_argument("--pattern", metavar='p', help="Provides a sub-pattern to look for")
	args = parser.parse_args()

	if len(args.docfiles) < 2:
		print "ERROR : at least 2 documents must be provided"
		sys.exit(0)

	show_version()

	# For each file, build a list of markers present
	filelist = args.docfiles

	markers = []

	for fil in filelist:
		if get_file_type(fil) == "docx":
			parser = docxManager.Reader(fil)

			try:
				path, markers = parser.launchParse()
			except AttributeError:
				print colored.red("ERROR :")
				sys.exit(-1)

			head, tail = ntpath.split(fil)
			print colored.yellow("Markers of file %s saved in %s"%(tail or ntpath.basename(head), path))

	print colored.green("\nTraceability matrix Successfully created")
