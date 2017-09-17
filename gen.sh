#!/bin/bash

if [ "$1" = "" ]; then
	echo "USAGE: ./gen.sh [yesterday | YYYY-MM-DD]"
	exit 1
elif [ "$1" = "yesterday" ]; then
	dt=$(date -v "-1d" "+%Y-%m-%d")
else
	dt=$1
fi

echo "Generating house 99 data files for $dt..."

scp pi@RAE.local:/RAE/raw/*_${dt}.csv ./raw/

./wrangle_power.py 99 1 no-header $dt

./wrangle_daily.py 99 1 no-header $dt
