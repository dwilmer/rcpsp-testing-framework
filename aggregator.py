#! /usr/bin/python

import sys, getopt
from dataset import Dataset

opts, args = getopt.getopt(sys.argv[1:], 'o:')

aggregate = Dataset()
for arg in args:
	aggregate.append(Dataset(arg, separator=':', header=False).pivot(), False)

opts = {k:v for (k, v) in opts}

if '-o' in opts:
	aggregate.export(opts['-o'])
else:
	print " | ".join(aggregate.headers)
	for row in aggregate.rows:
		print " | ".join(row[x] for x in aggregate.headers)
