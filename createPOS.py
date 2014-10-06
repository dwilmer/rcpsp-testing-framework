from chainer import chain
from flexopt import flexopt

def createPOS(data):
	options = data['options']
	chainOption = options['chainer']
	if chainOption == 'flow_opt' or chainOption == 'flow_opt_infer':
		return flexopt(data)
	else:
		return chain(data)


