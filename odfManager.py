import xml.dom.minidom

import re
import ntpath
import zipfile


class Reader:
	markers = []

	# OK
	def isValidDocxFile(self):
		if zipfile.is_zipfile(self.filename) == False:
			return False

		return True

	# OK
	def showManifest(self):
		for s in self.filelist:
			#print s.orig_filename, s.date_time,
			s.filename, s.file_size, s.compress_size
			if len(s.filename.split(".")) >= 2 and s.filename.split(".")[-1] == "xml":
				print s.filename

	def getRawContents(self):
		ostr = self.m_document.read('content.xml')
		raw = re.sub("<.*?>", "", ostr)

		self.rawText = raw

	def getContents(self):
		"""
		Just read the paragraphs from an XML file.
		"""
		ostr = self.m_document.read('content.xml')
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


	def findIt(self, name):
		self.markers = []

		i = 0
		while i >= 0:
			(tmp, i) = self.getMarker(self.rawText, name, i)
			if i > 0:
				self.markers.append(tmp.encode('utf-8'))


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


	# OK
	def launchParse(self):
		if not self.isValidDocxFile():
			raise AttributeError("Provided document is not a valid ODF file (%s)"%(self.filename))

		head, tail = ntpath.split(self.filename)
		if tail:
			outname = "tmp/" + tail[:-3] + "mark"
		else:
			outname = "tmp/" + ntpath.basename(head)[:-3] + "mark"

		outfil = open(outname, "w+")

		self.getRawContents()
		self.findIt("")

		self.fillMarkers(self.markers)

		for marker in self.markers:
			outfil.write(marker + "\n")

		outfil.close()

		return outname, self.markers

	# OK
	def __init__(self, filename):
		self.filename = filename
		self.m_document = zipfile.ZipFile(filename)
		self.filelist = self.m_document.infolist()