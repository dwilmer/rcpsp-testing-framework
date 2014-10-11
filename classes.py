#! /usr/bin/python

import sys, string
import Activity
import Instance
import Solution

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

	def readFromFile(self, filename):
		infile = open(filename, 'r')
		for line in infile:
			parts = line.split(':')
			if len(parts) == 2:
				self.results[parts[0]] = map(float, parts[1].split())
		infile.close()
		
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

	def readFromFile(self, filename):
		infile = open(filename, 'r')
		for line in infile:
			parts = line.split(':')
			if len(parts) == 2:
				self.addFinding(parts[0], float(parts[1]))
		infile.close()


