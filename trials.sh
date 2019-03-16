set -eu
trials=100
run=1
seed=1234
dir=logs/g3
mkdir -p "$dir"
failure=0.15
for quorum in 1.00 .90 .80 .70 .60; do
    for i in {1..$trials}; do
        nodes=25 zsh runner.sh --seed=$seed --quorum=$quorum --failure=$failure |& tee "$dir"/run-$run-q${quorum/./}-f${failure/./}-r3-trial$i.log
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
