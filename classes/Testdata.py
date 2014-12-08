#! /usr/bin/python

class Testdata:
	def __init__(self, pos):
		self.pos = pos
		self.results = {}

	def addTest(self, delayfilename):
		from solver import solve
		f = open(delayfilename, 'r')
		delays = map(float, list(f))
		f.close()

		delayedProblem = self.pos.clone()
		for (index, act) in enumerate(delayedProblem.activities):
			act.time *= delays[index]
			
		toSolve = {'options':{'solver':"noResources"},'instance':delayedProblem}
		delayedSolution = solve(toSolve)

		self.results[delayfilename] = delayedSolution.startTimes

	def writeToFile(self, filename):
		outfile = open(filename, 'w')
		for (delayfile, schedule) in self.results.iteritems():
			outfile.write(delayfile)
			outfile.write(':')
			outfile.write(' '.join(map(str, schedule)))
			outfile.write('\n')
		outfile.close()

	@staticmethod
	def readFromFile(filename, dataLib):
		newTestdata = Testdata(dataLib['pos'])
		infile = open(filename, 'r')
		for line in infile:
			parts = line.split(':')
			if len(parts) == 2:
				newTestdata.results[parts[0]] = map(float, parts[1].split())
		infile.close()
		return newTestdata

