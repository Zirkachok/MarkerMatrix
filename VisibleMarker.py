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

from xlwt import Workbook


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


def show_version(mode):
	print colored.blue(__doc__)
	print colored.blue("Version V" +__version__ + " ; License "+__license__+" ; "+mode+"\n")


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

	return path, markers


def hierarchy_mode():
	outFil = open("tmp/result.txt", "w")

	tmpID = ""

	markDict = {}

	# List nodes and their markers list
	tree = etree.parse("hierarchy.xml")
	for phase in tree.xpath("/Model/Phase"):

		for system in phase:
			# Single-document system
			if len(system) == 1:
				tmpID = phase.get("ID") + "." + system[0].get("ID")

				for elem in system[0]:
					if elem.tag == "Path":
						tmpMarkPath, tmpMarkerList = extract_markers(elem.text)

				if tmpID in markDict:
					sys.exit(-1)

				markDict[tmpID] = tmpMarkerList

			else:
				tmpID = phase.get("ID") + "." + system.get("ID")

				tmpSysMark = []

				for elem in system:
					if elem.tag == "Req":
						pass
					elif elem.tag == "Doc":
						tmpID = phase.get("ID") + "." +elem.get("ID")

						for detail in elem:
							if detail.tag == "Path":
								tmpMarkPath, tmpMarkerList = extract_markers(detail.text)

						if tmpID in markDict:
							sys.exit(-1)

						markDict[tmpID] = tmpMarkerList
						tmpSysMark = list(set(tmpSysMark).union(tmpMarkerList))

					else:
						pass

				markDict[phase.get("ID") + "." + system.get("ID")] = tmpSysMark


	# Test requirements
	tree = etree.parse("hierarchy.xml")
	for phase in tree.xpath("/Model/Phase"):
		outFil.write("Phase %s (%s) : \n"%(phase.get("name"), phase.get("ID")))
		print colored.blue("Phase %s (%s) : "%(phase.get("name"), phase.get("ID")))

		for system in phase:
			tmpID = ""
			# Single-document system
			if len(system) == 1:
				tmpID = phase.get("ID") + "." + system[0].get("ID")
				outFil.write("\t" + tmpID + "\n")
				print colored.yellow("\t" + tmpID)
			else:
				tmpID = phase.get("ID") + "." + system.get("ID")
				outFil.write("\t" + tmpID + "\n")
				print colored.yellow("\t" + tmpID)

				for doc in system:
					if doc.tag == "Doc":
						outFil.write("\t\t" + phase.get("ID") + "." + doc.get("ID") + "\n")
						print colored.yellow("\t\t" + phase.get("ID") + "." + doc.get("ID"))

						for elem in doc:
							if elem.tag == "Req":
								missings = []
								for mark in markDict[elem.text]:
									if mark not in markDict[phase.get("ID") + "." + doc.get("ID")]:
										missings.append(mark)
										outFil.write("\t\t\t" + mark + "\n")
										print colored.red("\t\t\t" + mark)

								if len(missings) == 0:
									outFil.write("\t\t\tReq %s : requirement fulfilled\n"%(elem.text))
									print colored.green("\t\t\tReq %s : requirement fulfilled"%(elem.text))
								else:
									outFil.write("\t\t\tReq %s : %d markers missing\n"%(elem.text, len(missings)))
									print colored.red("\t\t\tReq %s : %d markers missing"%(elem.text, len(missings)))

					elif doc.tag == "Req":
						missings = []
						for mark in markDict[doc.text]:
							outFil.write(phase.get("ID") + "." + system.get("ID") + "\n")
							if mark not in markDict[phase.get("ID") + "." + system.get("ID")]:
								# missings.append(mark)
								outFil.write("\t\t" + mark + "\n")
								print colored.red("\t\t" + mark)

						if len(missings) == 0:
							outFil.write("\t\tReq %s : requirement fulfilled\n"%(doc.text))
							print colored.green("\t\tReq %s : requirement fulfilled"%(doc.text))
						else:
							outFil.write("\t\tReq %s : %d markers missing\n"%(doc.text, len(missings)))
							print colored.red("\t\tReq %s : %d markers missing"%(doc.text, len(missings)))
					else:
						print colored.red("ERROR : Unknow node type %s"%(doc.tag))
						sys.exit(-1)

	outFil.close()

	print colored.green("\nTraceability matrix Successfully created")

	create_RTM(markDict)


def create_RTM(markersDict):
	lst = []

	# os.remove("VisibleMatrix-RTM.xls")

	book = Workbook()
	
	matrix = book.add_sheet('Traceability Matrix')

	i=1
	for ids in markersDict:
		lst = list(set(lst).union(markersDict[ids]))
		matrix.write(0, i, ids)
		i+=1

	i=1
	for mark in lst:
		matrix.write(i, 0, mark)
		i+=1

	# ligne1 = feuil1.row(1)
	# ligne1.write(0,'1')
	# ligne1.write(1,'235.0')
	# ligne1.write(2,'424.0')
	# ligne1.write(3,'a')

	matrix.col(0).width = 10000

	book.save("VisibleMatrix-RTM.xls")


if __name__ == '__main__':

	# Documents provided in arguments : compare them
	if len(sys.argv) >= 4 and (sys.argv[1] == "--compare" or sys.argv[1] == "-c"):
		show_version("Files comparison mode")
		sys.exit(0)
	elif len(sys.argv) >= 2 and (sys.argv[1] == "--model" or sys.argv[1] == "-m"):
		show_version("Model-based full testing mode")
		hierarchy_mode()
	else:
		print "USAGE : %s [-c FILE1 ... FILEn] [-h]"%(sys.argv[0])

		print "Comparison mode"
		print "\t--compare, -c : compare files provided in arguments"

		print "Automated mode"
		print "\t--model, -m : fetches the doc model and tests compliance"

		sys.exit(-1)
