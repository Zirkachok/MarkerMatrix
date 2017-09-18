import re
import ntpath
import zipfile

class Reader:
	markers = []

	def isValidDocxFile(self):
		if zipfile.is_zipfile(self.filename) == False:
			return False

		return True

	def showManifest(self):
		for s in self.filelist:
			#print s.orig_filename, s.date_time,
			s.filename, s.file_size, s.compress_size
			if len(s.filename.split(".")) >= 2 and s.filename.split(".")[-1] == "xml":
				print s.filename

	def removeXmlPattern(self, str, patternIn, patternOut):
		out = str

		start = out.find(patternIn)
		end = out[start+len(patternIn):].find(patternOut) + start+len(patternIn)

		# print '++ %s :: %s ;; %d :: %d'%(patternIn, patternOut, start, end+len(patternOut))

		while start >= 0 and end >= 0:
			if(end+len(patternOut) <= start):
				print '?? %s :: %s ;; %d :: %d'%(patternIn, patternOut, start, end+len(patternOut))
				return out

			out = out[:start] + out[end+len(patternOut):]

			start = out.find(patternIn)
			end = out[start+len(patternIn):].find(patternOut) + start+len(patternIn)

			# print '-- %s :: %s ;; %d :: %d'%(patternIn, patternOut, start, end+len(patternOut))

		return out

	def listMarkers(self, str):
		lst = []
		out = str

		start = out.find('[')
		end = out.find(']')

		while start >= 0 and end >= 0:
			lst.append(out[start:end+1])
			out = out[end+1:]
			start = out.find('[')
			end = out.find(']')

		return lst

	def launchParse(self):
		if not self.isValidDocxFile():
			raise AttributeError("Provided document is not a valid DOCX file (%s)"%(self.filename))

		ostr = self.m_document.read("word/document.xml")

		ostr = self.removeXmlPattern(ostr, "<?", "?>")
		ostr = self.removeXmlPattern(ostr, "<w:", ">")
		ostr = self.removeXmlPattern(ostr, "</w:", ">")
		ostr = self.removeXmlPattern(ostr, "<mc:", ">")
		ostr = self.removeXmlPattern(ostr, "<a:", ">")
		ostr = self.removeXmlPattern(ostr, "<v:", ">")


		head, tail = ntpath.split(self.filename)
		if tail:
			outname = "tmp/" + tail[:-4] + "mark"
		else:
			outname = "tmp/" + ntpath.basename(head)[:-4] + "mark"

		outfil = open(outname, "w+")

		lst = self.listMarkers(ostr)

		for marker in lst:
			outfil.write(marker + "\n")

		outfil.close()

		return outname, lst


	def __init__(self, filename):
		self.filename = filename
		self.m_document = zipfile.ZipFile(filename)
		self.filelist = self.m_document.infolist()
