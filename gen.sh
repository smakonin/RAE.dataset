#!/bin/bash

if [ "$1" = "" ]; then
	echo "USAGE: ./gen.sh [yesterday | YYYY-MM-DD]"
	exit 1
elif [ "$1" = "yesterday" ]; then
	dt=$(date -v "-1d" "+%Y-%m-%d")
else
	dt=$1
fi

echo "Copying remote data files for $dt..."
scp pi@RAE.local:/RAE/raw/*_${dt}.csv ./raw/house2/
#wc -l *_${dt}.csv

echo "Generating house 2 data files for $dt..."
./wrangle_power.py 2 1 no-header $dt 21
#./wrangle_daily.py 2 1 no-header $dt 21
