for x in $(ip route show | awk '/^[1-9]/ {print $1}'); do
  ipcalc $x | awk '/^Broadcast/ {print $2}';
done > broadcast.txt
