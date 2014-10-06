#! /user/bin/python

import os
from solver import solve
from classes import Testdata

def test(data):
	folder = '../datasets/delays/{0}/'.format(data['options']['testset'])
	testdata = Testdata(data['pos'])

	for delayset in os.listdir(folder):
		testdata.addTest(folder + '/' + delayset)

	return testdata

def testFromFile(data, inputfile):
	f = open(inputfile, 'r')
	delays = map(float, list(f))
	f.close()

	delayedProblem = data['pos'].clone()
	for (index, act) in enumerate(delayedProblem.activities):
		act.time *= delays[index]
	
	toSolve = {'options':{'solver':"noResources"},'instance':delayedProblem}
	delayedSolution = solve(toSolve)

	(numDelays, totalDelay) = getTaskDelays(data['solution'], delayedSolution)
	
	horizon = float(data['instance'].getHorizon())
	delayedMakespan = delayedSolution.getMakespan()
	originalMakespan = data['solution'].getMakespan()
	
	result = {}
	result['numDelays'] = numDelays
	result['totalDelay'] = totalDelay
	result['delayedPortion'] = float(numDelays) / float(len(data['instance'].activities))
	result['normTaskDelay'] = float(totalDelay) / horizon
	result['mksInc'] = delayedMakespan - originalMakespan
	result['relMksInc'] = float(delayedMakespan - originalMakespan) / float(originalMakespan)
	result['normMksInc'] = float(delayedMakespan - originalMakespan) / horizon
	return result

def getTaskDelays(originalSolution, delayedSolution):
	numDelays = 0
	totalDelay = 0

	for (i, orig) in enumerate(originalSolution.startTimes):
		delayed = delayedSolution.startTimes[i]
		if delayed > orig:
			numDelays += 1
			totalDelay += delayed - orig
	return (numDelays, totalDelay)

	
