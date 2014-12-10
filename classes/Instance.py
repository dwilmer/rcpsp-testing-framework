#! /usr/bin/python

import string
from Activity import Activity

# Class representing an RCPSP Instance
# Fields:
#  resources: an array of integers, representing resource availability
#  activities: an array of activities, with the indices doubling as IDs.
#  name: a name, for clarity when examining the instances
class Instance:
	def __init__(self):
		self.resources = []
		self.activities = []
		self.name = "new instance"

	def reverse(self):
		"""Reverses the order of activities"""
		for act in self.activities:
			act.reverse()

	def calculateFlex(self):
		self.addTransitiveConstraints()
		numConnections = self.countConstraints()
		self.removeTransitiveConstraints()

		n = len(self.activities)
		maxConnections = (n * (n - 1)) / 2
		return float(maxConnections - numConnections) / maxConnections

	def addPrecedenceConstraint(self, firstId, secondId):
		self.activities[firstId].successors.add(secondId)
		self.activities[secondId].predecessors.add(firstId)

	def removePrecedenceConstraint(self, firstId, secondId):
		try:
			self.activities[firstId].successors.remove(secondId)
			self.activities[secondId].predecessors.remove(firstId)
		except KeyError:
			pass

	def clone(self):
		pos = Instance()
		pos.name = "clone of " + self.name
		for act in self.activities:
			newAct = Activity(act.time, len(self.resources))
			newAct.resources = act.resources[:]
			newAct.predecessors = act.predecessors.copy()
			newAct.successors = act.successors.copy()
			pos.activities.append(newAct)

		return pos

	def getHorizon(self):
		return sum([act.time for act in self.activities])

	def getTopologicalOrdering(self):
		ordering = []
		numPreds = [len(act.predecessors) for act in self.activities]
		todo = [x for (x, n) in enumerate(numPreds) if n == 0]

		while todo:
			actId = todo.pop()
			ordering.append(actId)
			for succ in self.activities[actId].successors:
				numPreds[succ] -= 1
				if numPreds[succ] == 0:
					todo.append(succ)
		return ordering



	def addTransitiveConstraints(self):
		"""Adds all transitive constraints in O(n^3) time."""
		order = self.getTopologicalOrdering()
		n = len(order)
		for i in range(n):
			act_i = self.activities[order[i]]
			for j in range(i + 1, n):
				if order[j] in act_i.successors:
					act_j = self.activities[order[j]]
					for k in range(j + 1, n):
						if order[k] in act_j.successors:
							self.addPrecedenceConstraint(order[i], order[k])

	def removeTransitiveConstraints(self):
		"""Removes all transitive constraints in O(n^3) time."""
		n = len(self.activities)
		order = self.getTopologicalOrdering()
		for i in range(n):
			act_i = self.activities[order[i]]
			for j in range(i + 1, n):
				if order[j] in act_i.successors:
					act_j = self.activities[order[j]]
					for k in range(j + 1, n):
						if order[k] in act_j.successors:
							self.removePrecedenceConstraint(order[i], order[k])

	def countConstraints(self):
		return sum(map(lambda act: len(act.successors), self.activities))

	def calculateShortestDistances(self, target, addTaskLength = False):
		distances = [-1] * len(self.activities)
		todo = set()
		todo.add((target, 0))
		while(len(todo) > 0):
			(actId, distance) = todo.pop()
			if distances[actId] == -1 or distances[actId] > distance:
				distances[actId] = distance
				act = self.activities[actId]
				for succ in act.successors:
					if addTaskLength:
						todo.add((succ, distance + act.time))
					else:
						todo.add((succ, distance + 1))
				for pred in act.predecessors:
					if addTaskLength:
						predDistance = distance + self.activities[pred].time
						todo.add((pred, predDistance))
					else:
						todo.add((pred, distance + 1))
		return distances

	def getAllSuccessors(self, actId, successors = None):
		if successors == None:
			successors = [None] * len(self.activities)
		if not (successors[actId] == None):
			return successors[actId]
		actsucc = self.activities[actId].successors
		allsucc = reduce(set.union, map(lambda aId: self.getAllSuccessors(aId, successors), actsucc), actsucc)
		successors[actId] = allsucc
		return allsucc

	def getAllPredecessors(self, actId, predecessors = None):
		if predecessors == None:
			predecessors = [None] * len(self.activities)
		if not (predecessors[actId] == None):
			return predecessors[actId]
		actPred = self.activities[actId].predecessors
		allPred = reduce(set.union, map(lambda aId: self.getAllPredecessors(aId, predecessors), actPred), actPred)
		predecessors[actId] = allPred
		return allPred

	def containsPath(self, fromAct, toAct):
		return toAct in self.getAllSuccessors(fromAct)

	def exportToOpenedFile(self, outfile):
		outfile.write('%d,%s\n' % (len(self.resources), ','.join(map(str, self.resources))))
		for act in self.activities:
			outfile.write('%d,%s,%s\n' % (act.time, ' '.join(map(str, act.predecessors)),' '.join(map(str, act.resources))))

	def writeToFile(self, filename):
		f = file(filename, 'w')
		self.exportToOpenedFile(f)
		f.close()

	@staticmethod
	def readFromFile(filename, dataLib = None):
		# initialise intance
		newInstance = Instance()
		newInstance.name = filename

		# open file
		infile = open(filename, 'r')

		# use first line to detect type of file and read file
		firstLine = infile.readline()
		if firstLine.startswith("**********"):
			newInstance.readFromPSPLIB(infile)
		else:
			resLine = firstLine.split(',')
			if int(resLine[0]) > 0:
				newInstance.resources = map(int, resLine[1:])
			newInstance.readFromExport(infile)

		# close file handler, return the read instance
		infile.close()
		return newInstance
		
	def readFromExport(self, infile):

		line = string.strip(infile.readline())
		while not string.strip(line) == '':
			parts = line.split(',')
			newAct = Activity(int(parts[0]), 0)
			if len(parts[1]) > 0:
				newAct.predecessors.update(map(int, parts[1].split()))
			if len(parts[2]) > 0:
				newAct.resources = map(int, parts[2].split())
			self.activities.append(newAct)
			line = string.strip(infile.readline())

		for (actId, act) in enumerate(self.activities):
			for pred in act.predecessors:
				self.activities[pred].successors.add(actId)
	
	def readFromPSPLIB(self, infile):
		# skip first lines (not interesting)
		infile.readline()
		infile.readline()
		infile.readline()
		
		# read instance information (number of jobs, number of resources)
		(numJobs, numResources) = self.readInstanceInfo(infile)
		
		# set up arrays
		self.resources = [0] * numResources
		for i in range(numJobs):
			self.activities.append(Activity(0, numResources))
		
		# read precedence relations
		self.readPrecedences(infile)
		
		# read durations & resource cost
		self.readRequirements(infile)
		
		# read resource availability
		self.readResources(infile)


	def readInstanceInfo(self, infile):
		numJobs = 0
		numResources = 0
		while True:
			line = infile.readline()
			if line.startswith("*********************"):
				return (numJobs, numResources)
				
			parts = line.split(":  ")
			if parts[0].startswith("jobs"):
				numJobs = int(parts[1])
			if parts[0].startswith("  - renewable"):
				numResources = int(parts[1].split()[0])
	
	def readPrecedences(self, infile):
		# seek to header
		line = infile.readline()
		while not line.startswith("PRECEDENCE RELATIONS"):
			line = infile.readline()
		# skip one line
		infile.readline()
		
		#read precedence constraints
		line = infile.readline()
		while not line.startswith("***********"):
			parts = map(int, line.split())
			jobId = parts[0] - 1
			for successor in parts[3:]:
				self.addPrecedenceConstraint(jobId, successor -1)
			line = infile.readline()

	def readRequirements(self, infile):
		# seek to header
		line = infile.readline()
		while not line.startswith("REQUESTS/DURATIONS"):
			line = infile.readline()
		# skip two lines
		infile.readline()
		infile.readline()
		
		# read job requirements (time and resource usage)
		line = infile.readline()
		while not line.startswith("*********"):
			parts = map(int, line.split())
			jobId = parts[0] - 1;
			self.activities[jobId].time = parts[2]
			self.activities[jobId].resources = parts[3:]
			line = infile.readline()

	def readResources(self, infile):
		# seek to header
		line = infile.readline()
		while not line.startswith("RESOURCEAVAILABILITIES"):
			line = infile.readline()
		# skip one line
		infile.readline()
		
		# read resource availabilities
		line = infile.readline()
		self.resources = map(int, line.split()) 

	def printDebugInfo(self):
		print "Instance with %d jobs and %d resources" % (len(self.activities), len(self.resources))
		print "Resource capacities:"
		for cap in self.resources:
			print "  %d" % cap
		print "Jobs:"
		for i, job in enumerate(self.activities):
			print "  Job %d: length %d, %d predecessors, %d successors" % (i, job.time, len(job.predecessors), len(job.successors))
