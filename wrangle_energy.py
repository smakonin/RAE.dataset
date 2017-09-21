#! /usr/bin/env python3

#
# wrangle_energy.py -- Copyright (C) 2016-2017 Stephen Makonin
#

import os, sys
from operator import sub, truediv

def int32(lsw, msw):
    return msw * 0x10000 + lsw

print()
print('-----------------------------------------------------------------------------------------------')
print('Wrangle energy raw data files to store only power data  --  Copyright (C) 2016 Stephen Makonin.')
print('-----------------------------------------------------------------------------------------------')
print()

if len(sys.argv) != 6:
    print()
    print('USAGE: %s [house #] [block #] [header|no-header] [date, e.g., 2016-02-07] [sub-meters]' % (sys.argv[0]))
    print()
    exit(1)

house = int(sys.argv[1])
block = int(sys.argv[2])
header = True if sys.argv[3] == 'header' else False
date = sys.argv[4]
submeter_count = int(sys.argv[5])

raw_dir = './raw/house%d' % (house)
mains_file = '%s/IHD_%s.csv' % (raw_dir, date)
subs_file = '%s/SUB_%s.csv' % (raw_dir, date)

print('Checking for existance of file: %s' % (mains_file))
if not os.path.isfile(mains_file):
    print('\t ERROR: file does not exist!')
    exit(1)

print('\t Loading data...')
f_mains = open(mains_file, 'r')
mains_raw = list(f_mains)
f_mains.close()

print('Checking for existance of file: %s' % (subs_file))
if not os.path.isfile(subs_file):
    print('\t ERROR: file does not exist!')
    exit(1)

print('\t Loading data...')
f_subs = open(subs_file, 'r')
subs_raw = list(f_subs)
f_subs.close()

print('Converting mains data...')
mains_step1 = []
for l in mains_raw:
    l = l.strip()
    l = l.split(',')
    mains_step1.append(l)

print('Converting subs data (%d sub-meters)...' % submeter_count)
subs_step1 = []
for l in subs_raw:
    l = l.strip()
    l = l.split(',')
    for i in range(len(l)):
        if i != 1:
            l[i] = int(l[i])
    subs_step1.append(l)


meter_count = 8
circuit_count = meter_count * 3
final_file = './final/house%d_energy_blk%d.csv' % (house, block)

heading = 'unix_ts,mains,' + ','.join(['sub' + str(i) for i in range(1, submeter_count+1)])

seconds_per_day = 86400
hrs_step = 3600
mains_i = 0
offset = 2
count = 0
prev_ts = 0
mains = float(mains_step1[0][2])
ll = []
for subs_i in range(0, len(subs_step1), meter_count):
    ts = int(subs_step1[subs_i][0])

    #mains = ''
    if mains_i < len(mains_step1) and int(mains_step1[mains_i][0]) == ts:
        #mains = str(int(float(mains_step1[mains_i][1]) * 1000))
        mains = float(mains_step1[mains_i][2])
        mains_i += 1

    #print(ts, mains, ts % hrs_step)

    if ts % hrs_step != 0 and subs_i // meter_count < seconds_per_day - 1:
        prev_ts = ts
        continue

    l = [ts, mains]

    for i in range(meter_count):
        line = subs_step1[subs_i + i]

        if ord(line[1]) != ord('A') + i:
            print('\t ERROR: meter not equal at line', subs_i + i, ":", line)
            exit(1)

        #l += [str(line[7 + offset]), str(line[8 + offset]), str(line[9 + offset])]
        l += [int32(line[1 + offset], line[2 + offset]), int32(line[3 + offset], line[4 + offset]), int32(line[5 + offset], line[6 + offset])]


    ts_diff = ts - prev_ts - 1
    if prev_ts > 0 and ts_diff != 0:
        print('\t ERROR:', ts_diff, 'missing readings after ts ', ts)
        for i in range(ts_diff):
            new_ts = prev_ts + i + 1
            mains = ''
            if mains_i < len(mains_step1) and int(mains_step1[mains_i][0]) == new_ts:
                #mains = str(int(float(mains_step1[mains_i][1]) * 1000))
                mains = float(mains_step1[mains_i][2])
                mains_i += 1
            #f.write('%d,%s%s\n' % (new_ts, mains, ',' * submeter_count))
            ll.append([new_ts, mains] + [[]] * submeter_count)

    #f.write(','.join(l[:submeter_count+2]) + '\n')
    ll.append(l[:submeter_count+2])
    prev_ts = ts
    count += 1

print('Calculating and saving enegy data for smapling periods...')
f = open(final_file, 'a')
if header: f.write(heading + '\n')
for i in range(len(ll) - 1):
    l = list(map(truediv, map(sub, ll[i + 1], ll[i]), [1000] * len(ll[i])))
    l[0] = ll[i][0]
    l[1] = round(l[1] * 1000, 1)
    f.write(','.join([str(i) for i in l]) + '\n')
f.close()

print()
print('all done!')
print()
print()
