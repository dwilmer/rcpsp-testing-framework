#! /usr/bin/python

class Solution:
	def __init__(self, instance):
		self.instance = instance
		self.startTimes = [-1] * len(instance.activities)
		
	def readFromFile(filename, dataLib):
		newSolution = Solution(dataLib['instance'])

		infile = file(filename, 'r')
		line = infile.readline()
		newSolution.startTimes = map(float, line.split())
		infile.close()

		return newSolution

	def create(dataLib):
		return Solution(dataLib['instance'])

	def writeToFile(self, filename):
		out = file(filename, 'w')
		out.write(" ".join(map(str, self.startTimes)))
		out.write('\n')
		out.close()

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
