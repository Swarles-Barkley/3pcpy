nodes=20
coords=()
for n in {1..10}; do
    coords+=(--coord $n)
done
for n in {1..$nodes}; do
    python pcoord.py $coords $((n-1)) $nodes &
done
wait
