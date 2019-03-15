set -eu
trials=100
run=1
seed=1234
mkdir -p logs/g2/
for failure in 05 10 15 25 20 30; do
    for i in {1..$trials}; do
        nodes=25 zsh runner.sh --seed=$seed --quorum=0.96 --failure=0.$failure |& tee logs/g2/run-$run-q96-f$failure-r3-trial$i.log
        ((seed+=25))
    done
    ((run += 1))
done

# vary failure rate, node=25, coord=5, quorum=.90%, 
# gather time, bytes, success rate

# vary nodes, 
# 
