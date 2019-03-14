nodes=100
python pcoord.py $nodes &
for n in {1..$nodes}; do
    python pnode.py $((n-1)) $nodes &
done
wait
