#! /usr/bin/python
import sys, getopt, re, os.path, string
from collections import namedtuple
from multiprocessing import Pool
from classes.Instance import Instance
from classes.Activity import Activity
from classes.Report import Report
from classes.Solution import Solution
from classes.Testdata import Testdata
from solver import solve
from createPOS import createPOS
from tester import test
from reporter import report

Option = namedtuple('Option', 'key values default description')

optionConfig = {
	's': Option('solver', ['serial', 'parallel', 'serialFBI', 'parallelFBI', 'shortest'], 'serial', 'The solver to use'),
	'c': Option('chainer', [], 'random', 'The chainer to use'),
	't': Option('testset', [], 'exp2', 'The delay datacollection to use'),
	'o': Option('output', [], 'output', 'The folder to place output files.')
}

flagConfig = {
	'st': 'Disable pooling and use only one thread',
	'debug': 'Show debug data'
}

def showUsage():
	print '''This program reads RCPSP instances and converts them into a POS.
This is done using by solving the instance, creating an EST solution, and using that solution to create chains.

Usage: main.py (option|flag)* instance(s)
with instance(s) being the path(s) to one or more instance files.
'''
	print 'options:'
	for (key, option) in optionConfig.iteritems():
		if len(option.values) == 0:
			print '  -{0}:  {1.description}\n       Default value: {1.default}'.format(key, option)
		else:
			print '  -{0}:  {1.description}\n       Allowed values: {1.values} (default = {1.default})'.format(key, option)
	print
	print 'flags:'
	for flag, description in flagConfig.iteritems():
		print '  --{0}: {1}'.format(flag, description)

def getFilenames(instanceFilename):
	global options
	basename = os.path.basename(instanceFilename)
	outfolder = options['output']
	testsetname = options['testset'].replace("/",".")
	names = {
		'instance': instanceFilename,
		'solution': "{0}/solution/{1}.sol_{2}".format(outfolder, basename, options['solver']),
		'pos': "{0}/pos/{1}.sol_{2}.chain_{3}".format(outfolder, basename, options['solver'], options['chainer']),
		'testdata': "{0}/testdata/{1}.sol_{2}.chain_{3}.test_{4}".format(outfolder, basename, options['solver'], options['chainer'], testsetname),
		'report': "{0}/report/{1}.sol_{2}.chain_{3}.test_{4}.report".format(outfolder, basename, options['solver'], options['chainer'], testsetname)
	}
	return names


def processInstance(filename):
	global options

	# get data from files where available
	data = {'options': options}
	names = getFilenames(filename)
	data['instance'] = Instance()
	data['instance'].readFromFile(names['instance'])

	if os.path.isfile(names['solution']):
		data['solution'] = Solution(data['instance'])
		data['solution'].readFromFile(names['solution'])

		if os.path.isfile(names['pos']):
			data['pos'] = Instance()
			data['pos'].readFromDump(names['pos'])

			if os.path.isfile(names['testdata']):
				data['testdata'] = Testdata(data['pos'])
				data['testdata'].readFromFile(names['testdata'])

				if os.path.isfile(names['report']):
					data['report'] = Report()
					data['report'].readFromFile(names['report'])

	# get missing data, write to files
	if not 'solution' in data:
		data['solution'] = solve(data)
		data['solution'].writeToFile(names['solution'])
	if not 'pos' in data:
		data['pos'] = createPOS(data)
		data['pos'].export(names['pos'])
	if not 'testdata' in data:
		data['testdata'] = test(data)
		data['testdata'].writeToFile(names['testdata'])
	if not 'report' in data:
		data['report'] = report(data)
		data['report'].writeToFile(names['report'])

	print filename

def getOptions(flags):
	options = {}

	# set defaults
	for option in optionConfig.itervalues():
		options[option.key] = option.default
	for flag in flagConfig:
		options[flag] = False

	# get from flags
	for (lkey, value) in flags:
		key = lkey[1:] # strip leading '-'
		
		if key[0] == '-':
			# parse long options
			key = key[1:]
			options[key] = True
		else:
			option = optionConfig[key]
			if len(option.values) > 0:
				if value in option.values:
					options[option.key] = value
				else:
					print 'Warning: invalid value "{2}" for option {0}, using default ({1.default}). Allowed values: {1.values}.'.format(lkey, option, value)
			else:
				options[option.key] = value

	return options
	

def main():
	global options
	try:
		optionkeys = ''.join(['%s:' % x for x in optionConfig.iterkeys()])
		flags, args = getopt.getopt(sys.argv[1:], optionkeys, flagConfig.keys())
	except getopt.GetoptError as err:
		print str(err)
		showUsage()
		return 1

	if len(args) == 0:
		showUsage()
		return 1

	options = getOptions(flags)

	if options['st']: 
		map(processInstance, args)
	else:
		workers = Pool()
		workers.map(processInstance, args)

if __name__ == '__main__':
	sys.exit(main())

