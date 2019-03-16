set -eu
trials=100
run=1
seed=1234

mkdir -p logs/nodes

failure=.15
quorum=.90
for nodes in 5 10 15 20 25 30 35 40 45 50; do
    export nodes
    export numcoords=$(($nodes * 1 / 5))
    for i in {1..$trials}; do
        zsh runner.sh                              --seed=$seed --quorum=$quorum --failure=$failure |& tee logs/nodes/full-$run-q${quorum/./}-f${failure/./}-r3-trial$i.log
        zsh runner.sh --topology --topology-seed=$i --seed=$seed --quorum=$quorum --failure=$failure |& tee logs/nodes/rand-$run-q${quorum/./}-f${failure/./}-r3-topo$i-trial$i.log
        ((seed += nodes))
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
