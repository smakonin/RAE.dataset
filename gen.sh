#!/bin/bash

if [ "$1" = "" ]; then
	echo "USAGE: ./gen.sh [yesterday | YYYY-MM-DD]"
	exit 1
elif [ "$1" = "yesterday" ]; then
	dt=$(date -v "-1d" "+%Y-%m-%d")
else
	dt=$1
fi
	
echo "Generating data files for $dt..."

scp pi@teald.local:TEALD/raw/*_${dt}.csv ./raw/

~/SourceCode/TEALD/power_wrangler.py $dt

~/SourceCode/TEALD/TEALD_wrangler.py $dt
