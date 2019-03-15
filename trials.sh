set -eu
trials=100
run=1
seed=1234
mkdir -p logs/topo2/
failure=0.15
for quorum in 1.00 .90 .80 .70 .60; do
    for i in {1..$trials}; do
        nodes=25 zsh runner.sh --topology --topology-seed=$i --seed=$seed --quorum=$quorum --failure=$failure |& tee logs/topo2/run-$run-q${quorum/./}-f${failure/./}-r3-topo$i-trial$i.log
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
