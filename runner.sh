: ${nodes:=25}
coords=()
for n in {0..4}; do
    coords+=(--coord $n)
done
for n in {1..$nodes}; do
    python pcoord.py $((n-1)) $nodes "$@" $coords &
done
wait
