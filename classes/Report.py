#! /usr/bin/python

class Report:
	def __init__(self):
		self.findings = {}

	def addFinding(self, name, value):
		self.findings[name] = value

	def writeToFile(self, filename):
		outfile = open(filename, 'w')
		for (key, value) in self.findings.iteritems():
			outfile.write('{0}:{1}\n'.format(key, value))
		outfile.close()

	def readFromFile(filename, dataLib = None):
		newReport = Report()
		infile = open(filename, 'r')
		for line in infile:
			parts = line.split(':')
			if len(parts) == 2:
				newReport.addFinding(parts[0], float(parts[1]))
		infile.close()

		return newReport

	def create(dataLib):
		return Report()


