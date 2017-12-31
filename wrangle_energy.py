#! /usr/bin/env python3

#
# wrangle_energy.py -- Copyright (C) 2016-2017 Stephen Makonin
#

import os, sys, time, pytz
from operator import sub, truediv
from datetime import datetime
from datetime import timedelta

def int32(lsw, msw):
    return msw * 0x10000 + lsw

def downfill(data, col):
    missing_count = 0
    val = data[0][col]
    if val is None:
        for i in range(len(data)):
            if data[i][col] is not None:
                val = data[i][col]
                break

    if val is None:
        print('ERROR: no starting val, abort!')
        exit(1)

    for i in range(len(data)):
        if data[i][col] is None:
            data[i][col] = val
            missing_count += 1
        else:
            val = data[i][col]

    return missing_count


print()
print('-----------------------------------------------------------------------------------------------')
print('Wrangle energy raw data files to store only power data  --  Copyright (C) 2017 Stephen Makonin.')
print('-----------------------------------------------------------------------------------------------')
print()

if len(sys.argv) != 9:
    print()
    print('USAGE: %s [house #] [block #] [header|no-header] [date, e.g., 2016-02-07] [# of days] [mains: 1,2 OR calc] [sub-meters] [interval]' % (sys.argv[0]))
    print()
    print('       interval - one of: 1min, 15min, 30min, 1hr, 1day')
    print()
    exit(1)

house = int(sys.argv[1])
block = int(sys.argv[2])
header = True if sys.argv[3] == 'header' else False

local_tz = pytz.timezone('America/Vancouver')
start_dt = local_tz.localize(datetime.strptime(sys.argv[4], '%Y-%m-%d'))

days_count = int(sys.argv[5])

mains = sys.argv[6]
calc_mains = True if mains == "calc" else False
mains = [int(i)-1 for i in mains.split(',')] if not calc_mains else []

submeter_count = int(sys.argv[7])

sec_in_day = 86400
intervals = {'1min': 60, '15min': 900, '30min': 1800, '1hr': 3600, '1day': 86400 }
interval = sys.argv[8]
sample_steps = intervals[interval]

raw_dir = './raw/house%d' % (house)
samples = []
for i in range(days_count):
    date = start_dt + timedelta(days=i)
    start_ts = int(date.timestamp())
    date = date.strftime('%Y-%m-%d')
    print('For date %s, start timestamp is %d' % (date, start_ts))

    ihd_file = '%s/IHD_%s.csv' % (raw_dir, date)
    print('Checking for existance of file: %s' % (ihd_file))
    if not os.path.isfile(ihd_file):
        print('\t ERROR: file does not exist!')
        exit(1)

    subs_file = '%s/SUB_%s.csv' % (raw_dir, date)
    print('Checking for existance of file: %s' % (subs_file))
    if not os.path.isfile(subs_file):
        print('\t ERROR: file does not exist!')
        exit(1)

    print('Creating empty 1Hz data structure...')
    counts_1Hz = []
    for i in range(sec_in_day):
        counts_1Hz.append([start_ts + i, None, 0] + [None for i in range(submeter_count)])

    print('Loading IHD file and converting data...')
    f_ihd = open(ihd_file, 'r')
    for line in f_ihd:
        row = line.strip().split(',')
        i = int(row[0]) - start_ts
        if i < 0 or i >= sec_in_day:
            print('ERROR: outside of ts/day range, i =', i)
            continue #exit(1)
        val = float(row[2])
        counts_1Hz[i][1] = val
    f_ihd.close()

    print('Down-fill missing ihd readings...')
    missing_count = downfill(counts_1Hz, 1)
    print(missing_count, 'missing values where down-filled.')

    print('Loading SUBS file and converting subs data (%d sub-meters)...' % submeter_count)
    offset = 3
    f_subs = open(subs_file, 'r')
    for line in f_subs:
        row = line.strip().split(',')

        i = int(row[0]) - start_ts
        if i < 0 or i >= sec_in_day:
            print('ERROR: outside of ts/day range, i =', i)
            continue #exit(1)
        sub_id = (ord(row[1]) - ord('A')) * 3

        if sub_id < submeter_count:
            counts_1Hz[i][offset + sub_id] = int32(int(row[3]), int(row[4]))

        sub_id += 1
        if sub_id < submeter_count:
            counts_1Hz[i][offset + sub_id] = int32(int(row[5]), int(row[6]))

        sub_id += 1
        if sub_id < submeter_count:
            counts_1Hz[i][offset + sub_id] = int32(int(row[7]), int(row[8]))
    f_subs.close()

    print('Fill-in of mains column...')
    for i in range(len(counts_1Hz)):
        if calc_mains:
            if None not in counts_1Hz[i][3:]:
                counts_1Hz[i][2] = sum([int(i) for i in counts_1Hz[i][3:]])
        else:
            for i in mains:
                if counts_1Hz[i][i+3] is not None:
                    counts_1Hz[i][2] += int(counts_1Hz[i][i+3])

    print('Down-fill missing subs readings...')
    missing_count = 0
    for sub_id in range(offset, submeter_count + offset):
        missing_count += downfill(counts_1Hz, sub_id)
    print(missing_count, 'missing values where down-filled.')

    print('Aggregating from 1Hz to %s...' % interval)
    samples += counts_1Hz[0::sample_steps]

samples += [counts_1Hz[-1]]
print('row count', len(samples))

meter_count = 8
circuit_count = meter_count * 3
final_file = './final/house%d_energy_blk%d.csv' % (house, block)
heading = 'unix_ts,ihd,mains,' + ','.join(['sub' + str(i) for i in range(1, submeter_count+1)])

print('Final mean/down-fill missing %s data...' % interval)
missing_count = 0
for i in range(len(samples)):
    for j in range(offset, submeter_count + offset):
        if counts_1Hz[i][j] is None:
            data_was_missing = True
            if i == 0:
                counts_1Hz[i][j] = counts_1Hz[i+1][j]
            elif i == len(counts_1Hz) - 1:
                counts_1Hz[i][j] = counts_1Hz[i-1][j]
            elif i < len(counts_1Hz) - 1 and counts_1Hz[i + 1][j] is None:
                counts_1Hz[i][j] = counts_1Hz[i-1][j]
            else:
                counts_1Hz[i][j] = (counts_1Hz[i-1][j] + counts_1Hz[i+1][j]) / 2
            missing_count += 1
print('Data was missing in', missing_count, 'data point(s).')

print('Calculating and saving enegy data for smapling periods (in %s)...' % final_file)
f = open(final_file, 'a')
if header: f.write(heading + '\n')
for i in range(len(samples) - 1):
    l = list(map(truediv, map(sub, samples[i + 1], samples[i]), [1000] * len(samples[i])))
    l[0] = samples[i][0]
    l[1] = round(l[1] * 1000, 1)
    f.write(','.join([str(i) for i in l]) + '\n')
f.close()

print()
print('all done!')
print()
print()
