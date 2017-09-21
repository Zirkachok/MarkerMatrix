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

import xlwt
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

	docList = []
	phaseDict = {}
	systemDict = {}

	# List nodes and their markers list
	tree = etree.parse("hierarchy.xml")
	for phase in tree.xpath("/Model/Phase"):
		phaseDict[phase.get("ID")] = phase.get("name")

		for system in phase:
			# Single-document system
			if len(system) == 1:
				tmpID = phase.get("ID") + "." + system[0].get("ID")
				docList.append((tmpID, system[0].get("name"), ""))

				for elem in system[0]:
					if elem.tag == "Path":
						tmpMarkPath, tmpMarkerList = extract_markers(elem.text)

				if tmpID in markDict:
					sys.exit(-1)

				markDict[tmpID] = tmpMarkerList

			else:
				tmpID = phase.get("ID") + "." + system.get("ID")
				systemDict[tmpID] = system.get("name")

				tmpSysMark = []

				for elem in system:
					if elem.tag == "Req":
						pass
					elif elem.tag == "Doc":
						tmpID = phase.get("ID") + "." +elem.get("ID")
						docList.append((tmpID, elem.get("name"), phase.get("ID") + "." + system.get("ID")))

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

	create_RTM(markDict, phaseDict, systemDict, docList)


def create_RTM(markersDict, phases, systems, docs):
	lst = []

	phasesDone = []

	book = Workbook()
	
	matrix = book.add_sheet('Traceability Matrix')

	defaultStyle = xlwt.easyxf('alignment: horizontal center, vertical center')
	phaseStyle = 'font: height 200, bold 1; alignment: horizontal center, vertical center; borders: left thick, right thick; pattern: pattern solid, fore_color '

	colors = ["white", "light_green", "orange", "yellow", "pale_blue", "blue"]

	matrix.col(0).width = 5000

	curPhase = ""
	startMerge = 0
	endMerge = 0

	curSys = ""
	startSys = 0
	endSys = 0

	markers = []

	i = 1
	colIndex = 0
	curStyle = xlwt.easyxf(phaseStyle + colors[colIndex])

	matrix.write(0, 0, "Phase", curStyle)
	matrix.write(1, 0, "System", curStyle)
	matrix.write(2, 0, "Document", curStyle)

	for ids in docs:
		tmpId, tmpName, tmpSys = ids

		for mark in markersDict[tmpId]:
			if mark not in markers:
				markers.append(mark)

		if (tmpId.split(".")[0]) not in phasesDone:
			curStyle = xlwt.easyxf(phaseStyle + colors[colIndex])

			if startMerge != 0 and endMerge != 0:
				matrix.write_merge(0, 0, startMerge, endMerge, curPhase, curStyle)

			startMerge = endMerge + 1
			curPhase = phases[(tmpId.split(".")[0])]

			phasesDone.append(tmpId.split(".")[0])
			colIndex += 1
			curStyle = xlwt.easyxf(phaseStyle + colors[colIndex])


		if tmpSys == "":
			matrix.write(1, i, "", curStyle)
			if curSys != "":
				matrix.write_merge(1, 1, startSys, endSys, systems[curSys], curStyle)
				curSys = tmpSys
				startSys = i
		else:
			if tmpSys != curSys:
				if curSys != "":
					matrix.write_merge(1, 1, startSys, endSys, systems[curSys], curStyle)
				
				curSys = tmpSys
				startSys = i

			endSys = i


		matrix.write(2, i, tmpName, curStyle)
		matrix.col(i).width = 10000
		i += 1
		endMerge += 1

	matrix.write_merge(0, 0, startMerge, endMerge, curPhase, curStyle)

	i = 3
	for mark in markers:
		matrix.write(i, 0, mark, defaultStyle)

		j = 0
		for ids in docs:
			tmpId, tmpName, tmpSys = ids

			j += 1
			if mark in markersDict[tmpId]:
				matrix.write(i, j, "X", defaultStyle)


		i += 1

	# font: height 400, bold 1, color red, italic 1, underline single;
	# alignment: horizontal center, vertical center;
	# borders: left thin, right thin, top thick, bottom thick, top_color green;
	# pattern: pattern solid, fore_color yellow'
	# num_format_str = 'YYYY-MM-DD'

	book.save("VisibleMatrix-RTM.xls")

def check_marker_unicity(path, model):
	print colored.yellow("Check unicity of markers %s in file %s\n"%(model, path))

	_, markList = extract_markers(path)

	missMark = []
	uniq = [x for i, x in enumerate(markList) if x not in markList[0:i]]
	for item in uniq:
		if item[0:len(model)+1] == ("[" + model):
			if markList.count(item) > 1:
				missMark.append((item, markList.count(item)))

	if len(missMark) == 0:
		print colored.green("No redundant markers found in document")
	else:
		print colored.red("Redundant markers present in document:")
		for item, times in missMark:
			print colored.red("\tMarker %s redundant (%d times)"%(item, times))


if __name__ == '__main__':

	# Documents provided in arguments : compare them
	if len(sys.argv) >= 4 and (sys.argv[1] == "--compare" or sys.argv[1] == "-c"):
		show_version("Files comparison mode")
		sys.exit(0)
	elif len(sys.argv) >= 2 and (sys.argv[1] == "--model" or sys.argv[1] == "-m"):
		show_version("Model-based full testing mode")
		hierarchy_mode()
	elif len(sys.argv) == 4 and (sys.argv[1] == "--unicity" or sys.argv[1] == "-u"):
		show_version("Marker unicity testing mode")
		check_marker_unicity(sys.argv[2], sys.argv[3])
	else:
		print "USAGE : %s [-c FILE1 ... FILEn] [-m] [-u FILE MARK]"%(sys.argv[0])

		print "Comparison mode"
		print "\t--compare, -c : compare files provided in arguments"

		print "Automated mode"
		print "\t--model, -m : fetches the doc model and tests compliance"

		print "Marker unicity mode"
		print "\t--unicity, -u : fetches the doc model and tests compliance"

		sys.exit(-1)
