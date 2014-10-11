#! /usr/bin/python

# Class representing an activity in an RCPSP instance.
# Fields:
#  time: duration of the activity
#  resources: an array representing the resource requirements
#  predecessors: a set of integers, representing ids of predecessors
#  successors: a set of integers, representing ids of successors
class Activity:
	def __init__(self, time, numResources):
		self.time = time
		self.resources = [0] * numResources
		self.predecessors = set()
		self.successors = set()

	def reverse(self):
		"""Changes predecessors to successors and vice versa"""
		tmp = self.predecessors
		self.predecessors = self.successors
		self.successors = tmp

