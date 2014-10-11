#! /usr/bin/python

import sys, string
import Activity
import Instance

class Solution:
	def __init__(self, instance):
		self.instance = instance
		self.startTimes = [-1] * len(instance.activities)
		
	def writeToFile(self, filename):
		out = file(filename, 'w')
		out.write(" ".join(map(str, self.startTimes)))
		out.write('\n')
		out.close()

	def readFromFile(self, filename):
		infile = file(filename, 'r')
		line = infile.readline()
		self.startTimes = map(float, line.split())
		infile.close()

	def getMakespan(self):
		return max([self.startTimes[x] + self.instance.activities[x].time for x in range(len(self.startTimes)) if self.startTimes[x] > -1])

	def getResourceUsage(self, time):
		# get list of active activities at that time slot
		acts = self.instance.activities
		active = [act for (x, act) in enumerate(acts) if self.startTimes[x] > -1 and self.startTimes[x] <= time and self.startTimes[x] + act.time > time]
		
		# calculate resource usage
		usage = [0] * len(self.instance.resources)
		for activity in active:
			usage = map(sum, zip(usage, activity.resources))
		
		return usage

	def reset(self):
		self.startTimes = [-1] * len(self.instance.activities)

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


