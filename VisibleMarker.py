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

from lxml import etree
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


def extract_markers(fil):
	"""
	Selects the appropriate parser and request an extraction of markers in the document
	"""

	if not os.path.isfile(fil):
		print colored.red("ERROR : Invalid file path %s !"%(fil))
		sys.exit(-1)

	if get_file_type(fil) == "docx":
		parser = docxManager.Reader(fil)
	elif get_file_type(fil) == "odt":
		parser = odfManager.Reader(fil)
	else:
		print colored.red("ERROR : Unrecognised format %s !"%(get_file_type(fil)))
		sys.exit(-1)

	try:
		path, markers = parser.launchParse()
	except AttributeError:
		print colored.red("ERROR !")
		sys.exit(-1)

	head, tail = ntpath.split(fil)
	print colored.yellow("Markers of file %s saved in %s"%(tail or ntpath.basename(head), path))

	return path, markers


if __name__ == '__main__':
	show_version()

	tmpName = ""
	tmpReq = []

	tree = etree.parse("hierarchy.xml")
	for phase in tree.xpath("/Model/Phase"):
		tmpPhase = phase.get("ID")
		print "Phase : %s ( %s )"%(phase.get("name"), phase.get("ID"))

		for system in phase:
			if system.get("ID") != None:
				print "System : %s ( %s )"%(system.get("name"), system.get("ID"))

			for doc in system:
				tmpPath = ""
				tmpMarker = ""
				tmpMarkPath = ""
				tmpMarkerList = []

				for elem in doc:
					if elem.tag == "Path":
						tmpPath = elem.text
					elif elem.tag == "Req":
						tmpReq.append(elem.tag)
					elif elem.tag == "Marker":
						tmpMarker = elem.tag

				tmpID = tmpPhase + "." + doc.get("ID")
				tmpMarkPath, tmpMarkerList = extract_markers(tmpPath)
				print "Doc %s -- ID %s -- Path %s"%(doc.get("name"), tmpID, tmpMarkPath)



	# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

	# for system in tree.xpath("/Phase/System"):
	# 	for doc in 
	# 	tmpName = doc.get("name")
	# 	tmpID = doc.get("ID")

	# 	for elem in doc:
	# 		if elem.tag == "Path":
	# 			tmpPath = elem.text
	# 		elif elem.tag == "Req":
	# 			tmpReq.append(elem.tag)
	# 		elif elem.tag == "Marker":
	# 			tmpMarker = elem.tag

	# 	tmpMarkPath, tmpMarkerList = extract_markers(tmpPath)
	# 	print colored.blue("System %s -- ID %s -- Path %s"%(doc.get("name"), doc.get("ID"), tmpPath))

	# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

	# Dict = ID, path, markers, req
	print colored.green("\nTraceability matrix Successfully created")
