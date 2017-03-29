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
import xml.dom.minidom
import re
from termcolor import colored, cprint


class OdfReader:
	markers = []

	def __init__(self,filename):
		"""
		Open an ODF file.
		"""
		self.filename = filename
		self.m_odf = zipfile.ZipFile(filename)
		self.filelist = self.m_odf.infolist()

	def showManifest(self):
		"""
		Just tell me what files exist in the ODF file.
		"""
		for s in self.filelist:
			#print s.orig_filename, s.date_time,
			s.filename, s.file_size, s.compress_size

	def getRawContents(self):
		ostr = self.m_odf.read('content.xml')
		raw = re.sub("<.*?>", "", ostr)

		self.rawText = raw

	def getContents(self):
		"""
		Just read the paragraphs from an XML file.
		"""
		ostr = self.m_odf.read('content.xml')
		doc = xml.dom.minidom.parseString(ostr)
		paras = doc.getElementsByTagName('text:p')
		print ostr
		# print "I have ", len(paras), " paragraphs "
		# self.text_in_paras = []
		self.text_in_paras = ""

		test = open("text.txt" , "w")

		for p in paras:
			for ch in p.childNodes:
				# print ch.nodeType
				if ch.nodeType == ch.TEXT_NODE:
					# self.text_in_paras.append(ch.data)
					# self.text_in_paras += ch.data.encode('utf-8')
					# print ch.data
					pass


	def findIt(self,name):
		self.markers = []

		i = 0
		while i >= 0:
			(tmp, i) = self.getMarker(self.rawText, name, i)
			if i > 0:
				self.markers.append(tmp.encode('utf-8'))


		# for s in self.text_in_paras:
		# 	tmps = s.encode('utf-8')
		# 	print tmps

		# 	if "["+name in tmps and "]" in tmps:
		# 		i = 0
		# 		while i >= 0:
		# 			(tmp, i) = self.getMarker(tmps, name, i)
		# 			if i > 0:
		# 				self.markers.append(tmp.encode('utf-8'))
		# 				if "[1-SRS-01200" in tmps:
		# 					print "HERE %s : %s"%(self.filename, tmps)


				# if "[1-SRS-00040-07]" in s:
				# 	print "HERE : %s"%(self.filename)

				# # self.markers.append(XXX)
				# self.markers.append(s.encode('utf-8'))

	def getMarkers(self):
		return self.markers

	def fillMarkers(self, lst):
		for elem in self.markers:
			if elem in lst:
				pass
			else:
				lst.append(elem)

	def getMarker(self, s, patt, beg):
		start = s.find("["+patt, beg)
		end = s.find("]", start)

		if start >= 0 and end > 0:
			return s[start:end+1], end+1
		else:
			return "", -1


if __name__ == '__main__':
	if len(sys.argv) < 4:
		print "Usage: %s PATTERN FILE1 FILE2 ..."%(sys.argv[0])
		sys.exit(0)
	else:
		print __doc__+"Version V"+__version__+" ; License "+__license__+'\n'

		pattern = sys.argv[1]
		filelist = []
		for x in xrange(2,len(sys.argv)):
			filelist.append(sys.argv[x])

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

		myodf = OdfReader(fil) # Create object.
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
