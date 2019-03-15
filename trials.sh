set -eu
trials=100
tag=$1
run=1
mkdir -p logs/g1/
for failure in 40 30 20 10 05; do
    for i in {1..$trials}; do
        nodes=25 zsh runner.sh --quorum=0.96 --failure=0.$failure |& tee logs/run-$tag-q96-f$failure-r3-trial$i.log
    done
    ((run += 1))
done

# vary failure rate, node=25, coord=5, quorum=.90%, 
# gather time, bytes, success rate

# vary nodes, 
# 
