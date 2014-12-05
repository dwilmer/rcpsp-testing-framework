from collections import namedtuple
from os.path import isFile

Job = namedtuple('Job', ['key', 'filename','read','createWrite'])
class Pipeline:
	def __init__(self):
		self.jobs = []

	def addJob(self, key, filename, read, createWrite):
		self.jobs.append(Job(key, filename, read, createWrite))

	def execute(self, dataLib):
		dirty = False
		for job in self.jobs:
			if isFile(job.filename) and not dirty:
				dataLib[job.key] = job.read(job.filename)
			else:
				dataLib[job.key] = job.createWrite(filename)
				dirty = True





