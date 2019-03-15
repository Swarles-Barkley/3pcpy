nodes=4
for n in {1..$nodes}; do
    python pcoord.py --coord 3 $((n-1)) $nodes &
done
wait
