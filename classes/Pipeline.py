from os.path import isfile
from collections import namedtuple

Job = namedtuple('Job', ['key', 'filename', 'theClass', 'create'])
class Pipeline:
	def __init__(self):
		self.jobs = []

	def addJob(self, key, filename, theClass, create):
		self.jobs.append(Job(key, filename, theClass, create))

	def execute(self, dataLib):
		dirty = False
		for job in self.jobs:
			if isfile(job.filename) and not dirty:
				dataLib[job.key] = job.theClass.readFromFile(job.filename, dataLib)
			else:
				instance = job.create(dataLib)
				instance.writeToFile(job.filename)
				dataLib[job.key] = instance
				dirty = True





