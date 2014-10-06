import random
from chainFilters import filterByTime, filterMaxCC, filterMinID, filterMaxSlack, filterMinSlack, filterNonDecreasedSlack, sequence, fallback

namedFilters = [
	('special', fallback([filterMaxCC, sequence([filterMinID, filterMinSlack]), sequence([filterNonDecreasedSlack, filterMinSlack]), filterMaxSlack])),
	('maxCC', filterMaxCC),
	('minIDminSlack', sequence([filterMinID,filterMinSlack])),
	('minID', filterMinID),
	('maxSlack', filterMaxSlack)
]

def chain(data):
	# get data
	instance = data['instance']
	solution = data['solution']
	options = data['options']

	# determine filters
	chainFilter = chooseFilters(options['chainer'], options['debug'])

	# create POS
	return chainPolicella(instance, solution, chainFilter, options['debug'])

def chooseFilters(chainOption, debug = False):
	command = chainOption
	filters = []
	while len(command) > 0:
		for (tag, filt) in namedFilters:
			if command.startswith(tag):
				if debug: print 'found tag:', tag
				filters.append(filt)
				command = command[len(tag):]
				break
		else: # if no commands were matched, break out of while loop
			break

	return sequence([filterByTime, fallback(filters)])

def chainPolicella(instance, solution, chainFilter, debug=False):
	# create ordering of activities
	timedActivities = sorted([(time, act) for (act, time) in enumerate(solution.startTimes)])

	# create POS
	pos = instance.clone()

	# set up data dictionary
	data = {'pos':pos, 'debug':debug, 'solution': solution}

	for (resId, resource) in enumerate(instance.resources):
		lastTimes = [0] * resource
		lastActs = [-1] * resource
		chains = range(resource)

		data['lastTimes'] = lastTimes
		data['lastActs'] = lastActs

		for (startTime, actId) in timedActivities:
			data['actId'] = actId
			data['time'] = startTime
			data['lastPredecessor'] = -1
			act = instance.activities[actId]
			req = act.resources[resId]
			for i in range(req):
				candidates = chainFilter(chains, data)
				if len(candidates) == 0:
					print "No candidates to choose!"
					print "Resource unit", i, "of", req
					print "Time:", startTime,
					print "LastTimes:", lastTimes
					print "LastActs:", lastActs
				chain = random.choice([x for x in candidates])
				if lastActs[chain] != -1:
					pos.addPrecedenceConstraint(lastActs[chain], actId)
				data['lastPredecessor'] = lastActs[chain]
				lastActs[chain] = actId
				lastTimes[chain] = startTime + act.time
	
	return pos

