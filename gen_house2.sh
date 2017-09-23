#!/bin/bash

#
# Generatet he final RAE dataset data from House 1
#
# Copyright (C) 2017 Stephen Makonin
#

house=2
submeters=21

blocks=1
block_dts=(2017-09-13)
block_days=(6)

for ((i=0; i<$blocks; i++))
do
    blk=$((i+1))
    echo "******** block ${blk} starts on $${block_dts[$i]} and has {block_days[$i]} days:"
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
        ./wrangle_power.py ${house} ${blk} ${hdr} ${dt} ${submeters}
        ./wrangle_energy.py ${house} ${blk} ${hdr} ${dt} ${submeters} 1hr
    done
done

echo "******** done!"
