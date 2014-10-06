for n in "30" "60" "90" "120"; do
	echo $n
	for solver in "serial"; do
		echo $solver
		
		for chainer in "random" "maxCC" "minID" "maxCCminID" "maxCCminIDmaxSlack" "maxCCminIDminSlackmaxSlack" "special"; do #"flow_opt" "flow_opt_infer" ; do
			echo $chainer
			for testset in "exp2" "gauss_1_02" "unif_80_5" "fixed_50_30"; do
				echo $testset
				# Run simulation, generate reports
				./main.py -s ${solver} -c ${chainer} -t ${testset} ../datasets/j${n}/j${n}*.sm
				# summarize reports
				infiles="output/report/j$n*.sm.sol_${solver}.chain_${chainer}.test_${testset}.report"
				outfile="output/summary/j${n}_${solver}_${chainer}_${testset}"
				./aggregator.py -o $outfile $infiles
			done
		done
	done
done

