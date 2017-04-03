#!/usr/bin/env python

"""
MarkerMatrix: Checks documentation markers in documents, and builds a traceability matrix
"""
__author__ = "Julien Beaudaux"
__email__ = "julienbeaudaux@gmail.com"
__version__ = "1.0"
__license__ = "GPL"

import sys, os, time
import zipfile
from termcolor import colored, cprint
import argparse
import odfManager


def is_valid_file(parser, arg):
	if not os.path.exists(arg):
		parser.error("The file %s does not exist!" % arg)
	else:
		return arg

def show_version():
	print __doc__+"Version V"+__version__+" ; License "+__license__+'\n'


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("docfiles", help="input document to test", metavar="FILE", nargs='+', type=lambda x: is_valid_file(parser, x))
	parser.add_argument("--pattern", metavar='p', help="Provides a sub-pattern to look for")
	args = parser.parse_args()

	if len(args.docfiles) < 2:
		print "ERROR : at least 2 documents must be provided"
		sys.exit(0)
	filelist = args.docfiles

	show_version()

	pattern = ""
	if args.pattern:
		print "Sub-pattern \"%s\" provided"%(args.pattern)
		pattern = args.pattern


	outMatrix = open("result.csv", "w")

	"""
	Find markers in documents
	"""
	allMarkers = []
	filMarkers = []

	for fil in filelist:
		outMatrix.write(";")
		outMatrix.write(fil)

		if not zipfile.is_zipfile(fil):
			print "ERROR : provided document is not an Open Document File"
			sys.exit(0)

		myodf = odfManager.Reader(fil) # Create object.
		# myodf.showManifest()   # Tell me what files we have here
		myodf.getRawContents()    # Get the raw paragraph text.
		myodf.findIt(pattern)  # find the phrase ...

		myodf.fillMarkers(allMarkers)

		tmp = []
		myodf.fillMarkers(tmp)

		filMarkers.append(tmp)
		# print tmp


	"""
	Cross check dictionaries and build CSV
	"""
	outMatrix.write("\n")

	allMarkers = set(allMarkers)

	miss = []
	missfil = []

	for elem in allMarkers:
		outMatrix.write("%s; "%(elem))
		for i in range(0, len(filelist)):
			if elem in filMarkers[i]:
				outMatrix.write("Y;")
			else:
				miss.append(elem)
				missfil.append(filelist[i])

				outMatrix.write("N;")
		outMatrix.write("\n")

	if len(miss) > 0:
		print "%d Markers found in %d files, %d missing in some files :"%(len(allMarkers), len(filelist), len(miss))
		for i in range(0, len(miss)):
			print '\t' + colored("%s"%(miss[i]), "blue") + " in " + colored("%s"%(missfil[i]), "yellow")
	else:
		print colored("%d Markers found in %d files, none missing."%(len(allMarkers), len(filelist)), "green")
