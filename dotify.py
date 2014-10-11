#! /usr/bin/python

import sys
from classes.Instance import Instance
import getopt


optiontupels, args = getopt.getopt(sys.argv[1:], "i:p:c:tr")
options = {key[1:]:value for (key,value) in optiontupels}

instance = Instance()
instance.readFromFile(options['i'])

if 'p' in options:
	pos = Instance()
	pos.readFromDump(options['p'])
	if 't' not in options:
		pos.removeTransitiveConstraints()
else:
	pos = instance

compare = pos
if 'c' in options:
	compare = Instance()
	compare.readFromDump(options['c'])
	if 't' not in options:
		compare.removeTransitiveConstraints()



print "digraph pos {"
for actId, act in enumerate(pos.activities):
	if 'r' in options:
		print "\tact_{0} [label=\"{0} {1}\"];".format(actId, act.resources)
	else:
		print "\tact_{0} [label=\"{0}\"];".format(actId)

	
	instancePred = instance.activities[actId].predecessors
	comparePred = compare.activities[actId].predecessors
	for pred in act.predecessors:
		if pred in instancePred:
			print "\tact_{0} -> act_{1};".format(pred,actId)
		elif pred in comparePred:
			print "\tact_{0} -> act_{1} [color=\"purple\"];".format(pred,actId)
		else:
			print "\tact_{0} -> act_{1} [color=\"red\"];".format(pred,actId)
	for pred in comparePred:
		if not (pred in instancePred or pred in act.predecessors):
			print "\tact_{0} -> act_{1} [color=\"blue\"];".format(pred,actId)

print "}"
