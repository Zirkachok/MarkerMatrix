import xml.dom.minidom
import zipfile
import re


class Reader:
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