##
## FILTER DEFINITIONS
## These filters take a set of chains and a data dictionary.
## They return a subset of the chains, based on the data
##
def filterByTime(chains, data):
	"Retains chains which are available at the time of the activity being scheduled"
	lastTimes = data['lastTimes']
	return {chain for chain in chains if lastTimes[chain] <= data['time']}

def filterMaxCC(chains, data):
	"Retains chains which have the latest activity in common with the previously selected chain"
	lastPredecessor = data['lastPredecessor']
	lastActs = data['lastActs']
	return {chain for chain in chains if lastActs[chain] == lastPredecessor}

def filterMinID(chains, data):
	"Retains chains of which the last activity is already a predecessor of the current activity"
	lastActs = data['lastActs']
	actId = data['actId']
	pos = data['pos']
	return {chain for chain in chains if pos.containsPath(lastActs[chain], actId)}

def filterMaxSlack(chains, data):
	"Retains the chains which would provide the most slack (or earliest end time)"
	lastTimes = data['lastTimes']
	earliestEndTime = min([lastTimes[chain] for chain in chains])
	return {chain for chain in chains if lastTimes[chain] == earliestEndTime}

def filterMinSlack(chains, data):
	"Retains the chains which would provide the lest slack (or latest end time)"
	lastTimes = data['lastTimes']
	latestEndTime = max([lastTimes[chain] for chain in chains])
	return {chain for chain in chains if lastTimes[chain] == latestEndTime}

def filterMinDistance(chains, data):
	"Retains chains such that the distance, in number of activities, between the last activity in the chain and the activity to be scheduled is minimal"
	actId = data['actId']
	lastActs = data['lastActs']
	pos = data['pos']
	
	distances = pos.calculateShortestDistances(actId)
	chainDistances = [distances[lastActs[chain]] for chain in chains]
	return {chain for chain in chains if distances[lastActs[chain]] == min(chainDistances)}

def filterMinAddedSucc(chains, data):
	"Retains the chains for which the number of added successors to that chain would be minimal"
	actId = data['actId']
	lastActs = data['lastActs']
	pos = data['pos']
	
	actSuccessors = pos.getAllSuccessors(actId)
	filteredActs = {lastActs[chain] for chain in chains}

	addedSuccessors = {act:len(actSuccessors - pos.getAllSuccessors(act)) for act in filteredActs}
	minAddedSuccessors = min(addedSuccessors.values())

	return {chain for chain in chains if addedSuccessors[lastActs[chain]] == minAddedSuccessors}

def filterNonDecreasedSlack(chains, data):
	"Retains the chains such that this activity does not decrease the slack of the last activity on the chain"
	actId = data['actId']
	lastActs = data['lastActs']
	pos = data['pos']
	solution = data['solution']
	time = data['time']

	finiteSlackActs = {lastActs[chain] for chain in chains if chain in lastActs and  len(pos.activities[lastActs[chain]].successors) > 0}
	chainActSlack = {act:min([solution.startTimes[succ] for succ in pos.activities[act].successors]) for act in finiteSlackActs}
	nonDecreasedSlackActs = {act for (act, succStart) in enumerate(chainActSlack) if succStart >= time}
	return {chain for chain in chains if lastActs[chain] in nonDecreasedSlackActs}


##
## FILTER BUILDING BLOCKS
## These are the basic filter building blocks, to be used by the filter function builders
##
def _identity(chains, data):
	"Returns the given set of chains"
	return chains

def _ite(chains, data, fif, fthen, felse):
	"""If-then-else for chain filters. Runs the 'fif' filter function on the set of chains.
	If it returns the empty set, the 'felse' filter us run on the original set of chains and that is returned.
	If it returns a set of one or more chains, this result is filterded by the 'fthen' function and the result returned."""
	test = fif(chains, data)
	if len(test) > 0:
		return fthen(test, data)
	else:
		return felse(chains, data)

def _chain(chains, data, f1, f2):
	"""Runs both the f1 and f2 filters on the set of chains. Note: if f1 returns the empty set, this is returned and f2 is not run"""
	temp = f1(chains, data)
	if len(temp) == 0:
		return set()
	return f2(temp, data)

##
## FILTER FUNCTION BUILDERS
## These functions take filter functions and build a larger composite function
##
def sequence(filters):
	"""Takes a sequence of filter functions and will return a function that executes these filters in the given order"""
	if len(filters) == 0:
		return _identity
	head = filters[0]
	if len(filters) == 1:
		return head
	tailfun = sequence(filters[1:])
	return lambda chains, data:  _chain(chains, data, head, tailfun)

def ifthenelse(fif, fthen = _identity, felse = _identity):
	"""Takes three filter functions and will return a function that executes the first filter, if the result is non-empty runs the second filter on that set, if the result of the first filter is empty, the third filter is executed on the original set of chains.
	Note that by default, the fthen and felse functions are the identity function."""
	return lambda chains, data : _ite(chains, data, fif, fthen, felse)

def fallback(filters):
	"""Takes a sequence of filter functions and will return an function that executes these filters in order until one returns a non-empty set; this set is returned
	If all of the filters produce an empty set, the original set is returned."""
	if len(filters) == 0:
		return _identity
	tailfun = fallback(filters[1:])
	return ifthenelse(filters[0], felse = tailfun)

