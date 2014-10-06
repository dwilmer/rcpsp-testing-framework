from gurobipy import *

def flexopt(data):
	instance = data['instance']
	solution = data['solution']
	options = data['options']

	chainOption = options['chainer']

	pos = instance.clone()
	inferTransitiveConstraints = (chainOption == 'flow_opt_infer')

	chainFlow(pos, solution, instance, inferTransitiveConstraints, debug = options['debug'])

	return pos
	

def chainFlow(pos, solution, instance, inferImplicitConstraints = False, debug = False):
	# set up gurobi model
	m = Model("flowmodel")
	if not debug:
		m.setParam(GRB.Param.OutputFlag, 0) # turn off output
	m.setParam(GRB.Param.TimeLimit, 15.0 * 60) # limit execution time to 15 minutes

	# create ordering of activities
	timedActivities = sorted(zip(solution.startTimes, range(len(solution.startTimes))))

	# maintain sets of predecessors, successors and current activities
	predecessors = set()
	current = set()
	successors = set(range(len(timedActivities)))

	# build model
	i = 0
	sourceLinks = [[] for x in range(len(instance.resources))]
	sinkLinks = [[] for x in range(len(instance.resources))]
	crossLinks = [([None] * len(timedActivities)) for x in range(len(timedActivities))]
	crossLinkVars = [([None] * len(timedActivities)) for x in range(len(timedActivities))]
	while i < len(timedActivities):
		# get time of next activities
		(time, _) = timedActivities[i]

		# Move items from current set to predecessor set that are done
		done = {act for act in current if (solution.startTimes[act] + instance.activities[act].time <= time)}
		predecessors |= done
		current -= done

		# Move items from succesor set to current set that start at the current time
		newActs = set()
		while i < len(timedActivities) and timedActivities[i][0] == time:
			newActs.add(timedActivities[i][1])
			i += 1
		current |= newActs
		successors -= newActs

		# build the gurobi model with new activities
		for newAct in newActs:
			createLinksForActivity(m, newAct, predecessors, successors, instance, sourceLinks, sinkLinks, crossLinks, crossLinkVars)

	# limit resource capacity
	for rId, cap in enumerate(instance.resources):
		addConstraint(m, [1.0] * len(sourceLinks[rId]), sourceLinks[rId], GRB.LESS_EQUAL, float(cap) + 0.01, "resource_{0}_cap".format(rId))
		addConstraint(m, [1.0] * len(sinkLinks[rId]), sinkLinks[rId], GRB.LESS_EQUAL, float(cap) + 0.01, "resource_{0}_cap".format(rId))

	# set existing links to 1
	for (actId, act) in enumerate(instance.activities):
		for succ in act.successors:
			if crossLinkVars[actId][succ] == None:
				if instance.activities[actId].time > 0:
					# should not happen, report
					print "Link from {0} to {1} is not present in model".format(actId, succ)
					print "Start time of {0}: {2}, end time of {0}: {3}, start time of {1}: {4}".format(actId, succ, solution.startTimes[actId], solution.startTimes[actId] + instance.activities[actId].time, solution.startTimes[succ])
			else:
				addConstraint(m, [1.0], [crossLinkVars[actId][succ]], GRB.EQUAL, 1.0, "constraint_{0}_{1}".format(actId, succ))
	
	# infer transitive connections
	if inferImplicitConstraints:
		n = len(instance.activities)
		for i in range(n):
			time_i, actId_i = timedActivities[i]
			end_i = time_i + instance.activities[actId_i].time
			for j in range(i + 1, n):
				time_j, actId_j = timedActivities[j]
				if end_i > time_j:
					continue
				end_j = time_j + instance.activities[actId_j].time
				for k in range(j + 1, n):
					time_k, actId_k = timedActivities[k]
					if end_j > time_k:
						continue
					# for i, j, k such that i before j and j before k: if i->j and j->k, i->k
					linkA = crossLinkVars[actId_i][actId_j]
					linkB = crossLinkVars[actId_j][actId_k]
					linkC = crossLinkVars[actId_i][actId_k]
					if linkA and linkB and linkC:
						addConstraint(m, [1.0, 1.0, -1.0], [linkA, linkB, linkC], GRB.LESS_EQUAL, 1.0, "inference_{0}_{1}_{2}".format(actId_i, actId_j, actId_k))

				


	m.update()

	m.optimize()

	if m.status == GRB.INFEASIBLE:
		raise Exception("Model infeasible")

	# read solution into POS
	for fromId, toIds in enumerate(crossLinkVars):
		for toId, var in enumerate(toIds):
			if not(var == None):
				if var.X > 0.5:
					pos.addPrecedenceConstraint(fromId, toId)

def createLinksForActivity(m, newAct, predecessors, successors, instance, sourceLinks, sinkLinks, crossLinks, crossLinkVars):
	resourceInLinks = [[] for x in range(len(instance.resources))]
	resourceOutLinks = [[] for x in range(len(instance.resources))]

	# source and sink links
	for rId, cap in enumerate(instance.resources):
		sourceLink = m.addVar(0.0, cap, 0, GRB.CONTINUOUS, "s_{0}_{1}".format(newAct, rId))
		sourceLinks[rId].append(sourceLink)
		resourceInLinks[rId].append(sourceLink)

		sinkLink = m.addVar(0.0, cap, 0, GRB.CONTINUOUS, "t_{0}_{1}".format(newAct, rId))
		sinkLinks[rId].append(sinkLink)
		resourceOutLinks[rId].append(sinkLink)

	# links from all possible predecessors
	for pred in predecessors:
		resourceLinks = createLink(m, instance, pred, newAct, crossLinks, crossLinkVars)
		map(list.append, resourceInLinks, resourceLinks)

	# links to all possible successors
	for succ in successors:
		resourceLinks = createLink(m, instance, newAct, succ, crossLinks, crossLinkVars)
		map(list.append, resourceOutLinks, resourceLinks)

	# set sum of in links = sum of out links = required capacity for the activity
	m.update()
	for rId, req in enumerate(instance.activities[newAct].resources):
		addConstraint(m, [1.0] * len(resourceInLinks[rId]), resourceInLinks[rId], GRB.EQUAL, float(req), "{0}_in_{1}_cap".format(newAct, rId))
		addConstraint(m, [1.0] * len(resourceOutLinks[rId]), resourceOutLinks[rId], GRB.EQUAL, float(req), "{0}_out_{1}_cap".format(newAct, rId))

def createLink(m, instance, fromId, toId, crossLinks, crossLinkVars):
	resourceLinks = []
	# create new if needed
	if crossLinks[fromId][toId] == None:
		# variable to register whether there is a link or not
		linkVar = m.addVar(0.0, 1.0, 1.0, GRB.BINARY, "{0}_{1}".format(fromId, toId))
		crossLinkVars[fromId][toId] = linkVar
		crossLinks[fromId][toId] = [None] * len(instance.resources)

		# for each resource create new variable
		totCap = 0
		for rId, cap in enumerate(instance.resources):
			resourceLink = m.addVar(0.0, float(cap), 0.0, GRB.CONTINUOUS, "{0}_{1}_{2}".format(fromId, toId, rId))
			crossLinks[fromId][toId][rId] = resourceLink
			resourceLinks.append(resourceLink)
			totCap += cap
		m.update()

		# force linkVar to 1 if any of the resource links is set
		links = resourceLinks[:]
		weights = [1.0] * len(links)

		links.append(linkVar)
		weights.append(-1.0 * totCap)

		addConstraint(m, weights, links, GRB.LESS_EQUAL, 0.01, "{0}_{1}_collector".format(fromId, toId))
	else:
		resourceLinks = crossLinks[fromId][toId][:]
	return resourceLinks

def addConstraint(model, weights, links, sign, rhs, name, debug=False):
	# add constraint
	model.addConstr(LinExpr(weights, links), sign, rhs, name)
	# debug
	if debug:
		lhs = " + ".join(map(lambda w, l: "%.0f*%s" % (w, l.VarName), weights, links))
		print lhs, sign, rhs, "(", name, ")"

