set -eu
trials=100
run=1
seed=1234
mkdir -p logs/topo1/
for failure in 05 10 15 20 25 30; do
    for i in {1..$trials}; do
        nodes=25 zsh runner.sh --topology --topology-seed=$i --seed=$seed --quorum=0.96 --failure=0.$failure |& tee logs/topo1/run-$run-q96-f$failure-r3-topo$i-trial$i.log
        ((seed+=25))
    done
    ((run += 1))
done

# vary failure rate, node=25, coord=5, quorum=.90%, 
# gather time, bytes, success rate

# vary nodes, 

# topology
# very difficult
# fix failure to something reasonable
# vary quorum
