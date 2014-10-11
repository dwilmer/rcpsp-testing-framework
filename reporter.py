#! /user/bin/python
from classes.Instance import Instance
from classes.Activity import Activity
from classes.Report import Report
from classes.Solution import Solution
from classes.Testdata import Testdata

def report(data):
	from solver import solve
	report = Report()

	reportInstanceProperties(report, data['instance'])
	reportInstanceStructure(report, data['instance'], 'instance')
	reportInstanceStructure(report, data['pos'], 'pos')

	solveData = {'options':{'solver':'noResources'},'instance':data['pos']}
	pos_est_schedule = solve(solveData)
	reportScheduleQuality(report, data['instance'], data['solution'], 'schedule')
	reportScheduleQuality(report, data['pos'], pos_est_schedule, 'pos_est_schedule')

	reportTestData(report, data)

	return report

# INSTANCE PROPERTIES
def reportInstanceProperties(report, instance):
	report.addFinding("horizon", instance.getHorizon())

# NETWORK STRUCTURE
def reportInstanceStructure(report, instance, prefix):
	report.addFinding(prefix + "_flex", instance.calculateFlex())
	report.addFinding(prefix + "_numConnections", instance.countConstraints())

# SCHEDULE PROPERTIES
def reportScheduleQuality(report, instance, schedule, prefix):
	report.addFinding(prefix + "_makespan", schedule.getMakespan())
	report.addFinding(prefix + "_avgRscUsg", calculateAverageResourceUsage(instance, schedule))
	reportChtourouMetrics(report, instance, schedule, prefix)
	reportRiskFactor(report, instance, schedule, prefix)
	reportTotalRoom(report, instance, schedule, prefix)

def reportChtourouMetrics(report, instance, schedule, prefix):
	# calculate metrics
	deadline = schedule.getMakespan()
	slack = map(lambda actId: calculateSlack(instance, schedule, actId, deadline), range(len(instance.activities)))
	alpha = [1 if s > 0 else 0 for s in slack]
	frac = float(sum(slack)) / instance.getHorizon()
	cappedSlack = map(min, slack, [act.time * frac for act in instance.activities])

	rawMetrics = map(chtourouMetricsSingleAct, instance.activities, slack, alpha, cappedSlack)
	metrics = reduce(lambda x,y: map(float.__add__, x, y), rawMetrics)
	
	# report metrics
	for i, metric in enumerate(metrics):
		report.addFinding("{0}_RB{1}".format(prefix, i + 1), metric)

def reportRiskFactor(report, instance, schedule, prefix):
	riskFactors = [-1] * len(instance.activities)
	calculateRiskFactor(instance, schedule, 0, riskFactors)
	report.addFinding(prefix + "_riskFactor", sum(riskFactors))

def reportTotalRoom(report, instance, schedule, prefix):
	report.addFinding(prefix + "_totalRoom", sum(map(lambda actId: sum(map(lambda succId: schedule.startTimes[succId] - schedule.startTimes[actId] - instance.activities[actId].time, instance.activities[actId].successors), 0), range(len(instance.activities))), 0))


def calculateRiskFactor(instance, schedule, actId, riskFactors):
	if riskFactors[actId] >= 0:
		return riskFactors[actId]
	riskFactor = 1
	act = instance.activities[actId]
	for succ in act.successors:
		succRiskFactor = calculateRiskFactor(instance, schedule, succ, riskFactors)
		riskFactor += succRiskFactor * (float(act.time + 1) / float(schedule.startTimes[succ] - schedule.startTimes[actId] + 1))
	riskFactors[actId] = riskFactor
	return riskFactor

def chtourouMetricsSingleAct(act, slack, alpha, cappedSlack, totalResources = 1):
	numSucc = len(act.successors)
	sumRes = sum(act.resources)
	metrics = []

	metrics.append(slack) #RB1
	metrics.append(slack * numSucc) #RB2
	metrics.append(slack * sumRes) #RB3
	metrics.append(slack * numSucc * sumRes) #RB4

	metrics.append(alpha) #RB5
	metrics.append(alpha * numSucc) #RB6
	metrics.append(alpha * sumRes) #RB7
	metrics.append(alpha * numSucc * sumRes) #RB8

	metrics.append(cappedSlack) #RB9
	metrics.append(cappedSlack * numSucc) #RB10
	metrics.append(cappedSlack * sumRes) #RB11
	metrics.append(cappedSlack * numSucc * sumRes) #RB12

	normRes = float(sumRes) / float(totalResources)
	metrics.append(slack * normRes)
	metrics.append(alpha * normRes)
	metrics.append(cappedSlack * normRes)

	return map(float, metrics)


def calculateSlack(instance, schedule, actId, deadline):
	act = instance.activities[actId]
	earliestFinishingTime = act.time + schedule.startTimes[actId]
	latestFinishingtime = deadline
	for succ in act.successors:
		if schedule.startTimes[succ] < latestFinishingtime:
			latestFinishingtime = schedule.startTimes[succ]
	return latestFinishingtime - earliestFinishingTime

def calculateAverageResourceUsage(instance, solution):
	if len(instance.resources) == 0:
		return 0
	timepoints = int(solution.getMakespan())
	resourceUsage = [0] * len(instance.resources)
	for t in range(timepoints):
		resourceUsage = map(int.__add__, resourceUsage, solution.getResourceUsage(t))
	avgResourceUsage = map(lambda tot, cap: float(tot) / float(cap * timepoints), resourceUsage, instance.resources)
	return sum(avgResourceUsage) / len(instance.resources)

# TEST DATA
def reportTestData(report, data):
	totals = {}
	for instance in data['testdata'].results.itervalues():
		instanceInfo = getTestInstanceInfo(report, data, instance)
		totals = {x: totals.get(x, 0) + instanceInfo[x] for x in instanceInfo}
	for fact, value in totals.iteritems():
		report.addFinding(fact, float(value) / len(data['testdata'].results))


def getTestInstanceInfo(report, data, instance):
	from solver import solve
	instanceInfo = {}

	delayedSolution = Solution(data['instance'])
	delayedSolution.startTimes = instance

	# gather data
	instanceInfo['makespan'] = delayedSolution.getMakespan()
	instanceInfo['numDelays'] = sum(map(float.__gt__, map(float, delayedSolution.startTimes), map(float,data['solution'].startTimes)))
	instanceInfo['totalDelay'] = sum(map(float.__sub__, map(float, delayedSolution.startTimes), map(float, data['solution'].startTimes)))
	
	return instanceInfo

