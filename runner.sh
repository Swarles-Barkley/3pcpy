: ${nodes:=25}
: ${numcoords:=5}
coords=()
for n in {1..$numcoords}; do
    coords+=(--coord $((n-1)) )
done
for n in {1..$nodes}; do
    python pcoord.py $((n-1)) $nodes "$@" $coords &
done
wait
