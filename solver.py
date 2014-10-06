from classes import *

def solve(data):
	instance = data['instance']
	options = data['options']
	solution = Solution(instance)
	if options['solver'] == 'noResources':
		solveSerial(solution, False)
	if options['solver'] == 'shortest':
		findBestSolver(solution)
	if options['solver'].startswith('serial'):
		solveSerial(solution)
	if options['solver'].startswith('parallel'):
		solveParallel(solution)
	if options['solver'].endswith('FBI'):
		improveFBI(solution)
	return solution

def findBestSolver(solution):
	solveSerial(solution)
	makespan = solution.getMakespan()
	startTimes = solution.startTimes

	improveFBI(solution)
	if solution.getMakespan() < makespan:
		makespan = solution.getMakespan()
		startTimes = solution.startTimes
	
	solution.reset()
	solveParallel(solution)
	if solution.getMakespan() < makespan:
		makespan = solution.getMakespan()
		startTimes = solution.startTimes

	improveFBI(solution)
	if solution.getMakespan() < makespan:
		makespan = solution.getMakespan()
		startTimes = solution.startTimes

	solution.startTimes = startTimes

def improveFBI(solution):
	orig_startTimes = solution.startTimes
	solution.instance.reverse()
	solution.reset()
	selector = lambda todo: findLatestAct(todo, solution.instance.activities, orig_startTimes, True)
	solveSerial(solution, selector = selector)

	reversed_startTimes = solution.startTimes
	solution.instance.reverse()
	solution.reset()
	selector = lambda todo: findLatestAct(todo, solution.instance.activities, reversed_startTimes, False)
	solveSerial(solution, selector = selector)

def findLatestAct(actIds, acts, startTimes, calcMax = True):
	latestTime = -1
	latestId = -1
	for listId, actId in enumerate(actIds):
		time = startTimes[actId]
		if calcMax:
			time += acts[actId].time
		if latestTime == -1 or (calcMax and time > latestTime) or ((not calcMax) and time < latestTime):
			latestTime = time
			latestId = listId
	return latestId

def solveParallel(solution, selector = lambda todo: 0):
	activities = solution.instance.activities
	resources = solution.instance.resources
	scheduledActs = set()
	time = 0
	while len(scheduledActs) < len(activities):
		eligible = parDetermineEligible(time, solution, scheduledActs)
		while len(eligible) > 0:
			candidate = eligible.pop(selector(eligible))
			nextAct = activities[candidate]
			if isFeasible(solution, nextAct, time):
				solution.startTimes[candidate] = time
				scheduledActs.add(candidate)
		time += 1

def parDetermineEligible(time, solution, scheduledActs):
	activities = solution.instance.activities
	startTimes = solution.startTimes
	eligibleActs = []
	for x, act in enumerate(activities):
		if x in scheduledActs:
			continue
		eligible = True
		for pred in act.predecessors:
			if not pred in scheduledActs:
				eligible = False
				break
			if startTimes[pred] + activities[pred].time > time:
				eligible = False
				break
		if eligible:
			eligibleActs.append(x)
	return eligibleActs


def solveSerial(solution, checkResources = True, selector = lambda todo: 0):
	activities = solution.instance.activities
	resources = solution.instance.resources
	todo = [x for (x, act) in enumerate(activities) if len(act.predecessors) == 0]
	scheduledActs = set()
	while len(todo) > 0:
		# Next activity to schedule
		nextIndex = todo.pop(selector(todo))
		nextAct = activities[nextIndex]
		
		# Find correct time
		time = latestPredecessorEndtime(solution, nextAct)
		if checkResources:
			while not isFeasible(solution, nextAct, time):
				time += 1
		
		solution.startTimes[nextIndex] = time
		scheduledActs.add(nextIndex)
		
		# Add successors to todo list (if applicable)
		todo += findEligableSuccessors(nextAct, activities, scheduledActs)

def latestPredecessorEndtime(solution, nextAct):
	time = 0
	acts = solution.instance.activities
	for pred in nextAct.predecessors:
		endTime = solution.startTimes[pred] + acts[pred].time
		if endTime > time:
			time = endTime
	return time

def isFeasible(solution, activity, time):
	for t in range(time, time + activity.time):
		resourceUsage = solution.getResourceUsage(t)
		for (i, cap) in enumerate(solution.instance.resources):
			if activity.resources[i] + resourceUsage[i] > cap:
				return False
	return True

def findEligableSuccessors(nextAct, activities, scheduledActs):
	eligable = []
	for succ in nextAct.successors:

		for i in activities[succ].predecessors:
			if not (i in scheduledActs):
				break
		else:
			eligable.append(succ)
	return eligable

