#! /bin/bash

function simulate {
	n=$1
	solver=$2
	chainer=$3
	testset=$4
	
	# Run simulation, generate reports
	./main.py -s ${solver} -c ${chainer} -t ${testset} ../datasets/j${n}/j${n}*.sm;
	# summarize reports
	infiles="output/report/j$n*.sm.sol_${solver}.chain_${chainer}.test_${testset}.report"
	outfile="output/summary/j${n}_${solver}_${chainer}_${testset}"
	./aggregator.py -o $outfile $infiles

}

# instance sets
sizes="30 60 90 120"

# solvers
solvers="serial"

# chainer sets
originalchainers="random maxCC minID maxCCminID"
gurobichainers="flow_opt flow_opt_infer"
slackchainers=" maxCCminIDmaxSlack maxCCminIDminSlackmaxSlack special"
flexchainers="maxCCminIDminChains maxCCminIDmaxChains maxCCminIDminChainsmaxChains"
flexchainers2="maxCCminIDminAddedPredecessors maxCCminIDminAddedPredecessors2"
proposals="flexopt_heuristic flexopt_transitive flexopt_transitive2"

# delay sets
delaysets="exp2 gauss_1_02 unif_80_5 fixed_50_30"
nodelay="none"

for n in $sizes; do
	echo $n
	for solver in $solvers; do
		echo $solver
		for chainer in "maxCCminID"; do
			echo $chainer
			for testset in "large"; do
				echo $testset
				simulate $n $solver $chainer $testset
			done
		done
	done
done

#for chainer in $gurobichainers ; do # only available for instance size 30
#	echo $chainer
#	for testset in "exp2" "gauss_1_02" "unif_80_5" "fixed_50_30"; do
#		simulate "30" "serial" ${chainer} ${testset}
#	done
#done

