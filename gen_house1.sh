#!/bin/bash

#
# Generatet he final RAE dataset data from House 1
#
# Copyright (C) 2017 Stephen Makonin
#

house=1
submeters=24

blocks=2
block_dts=(2016-02-07 2016-03-06)
block_days=(9 63)

for ((i=0; i<$blocks; i++))
do
    blk=$((i+1))
    echo "******** block ${blk} starts on ${block_dts[$i]} and has ${block_days[$i]} days:"
    for ((j=0; j<${block_days[$i]}; j++))
    do
        dt=$(date -j -f %Y-%m-%d -v+${j}d ${block_dts[$i]} +%Y-%m-%d)
        if [ "$j" = "0" ]; then
        	hdr="header"
        else
        	hdr="no-header"
        fi

        echo "******** processing data for ${dt}..."
        #./wrangle_daily.py ${house} ${blk} ${hdr} ${dt} ${submeters}
        ./wrangle_power.py ${house} ${blk} ${hdr} ${dt} calc ${submeters}
    done
    ./wrangle_energy.py ${house} ${blk} header ${block_dts[$i]} ${block_days[$i]} calc ${submeters} 1hr
done

echo "******** done!"
