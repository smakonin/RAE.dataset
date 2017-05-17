#! /usr/bin/env python3

#
# power_wrangler.py -- Copyright (C) 2016-2017 Stephen Makonin
#

import os, sys

def int32(lsw, msw):
    return msw * 0x10000 + lsw

print()
print('----------------------------------------------------------------------------------------------')
print('Wrangle daily raw data files to store only power data  --  Copyright (C) 2016 Stephen Makonin.')
print('----------------------------------------------------------------------------------------------')
print()

if len(sys.argv) != 5:
    print()
    print('USAGE: %s [house #] [block #] [header|no-header] [date, e.g., 2016-02-07]' % (sys.argv[0]))
    print()
    exit(1)

house = int(sys.argv[1])
block = int(sys.argv[2])
header = True if sys.argv[3] == 'header' else False
date = sys.argv[4]

raw_dir = './raw'
mains_file = '%s/EMU2_%s.csv' % (raw_dir, date)
subs_file = '%s/PS24_%s.csv' % (raw_dir, date)

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

print('Converting subs data...')
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
final_file = './final/house%d_power_blk%d.csv' % (house, block)
heading = 'unix_ts,mains,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24'

f = open(final_file, 'a')
if header: f.write(heading + '\n')

mains_i = 0
offset = 2
count = 0
prev_ts = 0
#mains = mains_step1[0][1]
for subs_i in range(0, len(subs_step1), meter_count):
    l = []

    ts = subs_step1[subs_i][0]
    l.append(str(ts))

    mains = ''
    if mains_i < len(mains_step1) and int(mains_step1[mains_i][0]) == ts:
        mains = str(int(float(mains_step1[mains_i][1]) * 1000))
        mains_i += 1
    l.append(mains)

    for i in range(meter_count):
        line = subs_step1[subs_i + i]

        if ord(line[1]) != ord('A') + i:
            print('\t ERROR: meter not equal at line', subs_i + i, ":", line)
            exit(1)

        l += [str(line[7 + offset]), str(line[8 + offset]), str(line[9 + offset])]

    ts_diff = ts - prev_ts - 1
    if prev_ts > 0 and ts_diff != 0:
        print('\t ERROR:', ts_diff, 'missing readings after ts ', ts)
        for i in range(ts_diff):
            new_ts = prev_ts + i + 1
            mains = ''
            if mains_i < len(mains_step1) and int(mains_step1[mains_i][0]) == new_ts:
                mains = str(int(float(mains_step1[mains_i][1]) * 1000))
                mains_i += 1
            f.write('%d,%s,,,,,,,,,,,,,,,,,,,,,,,,\n' % (new_ts, mains))

    f.write(','.join(l) + '\n')
    prev_ts = ts
    count += 1


f.close()

seconds_per_day = 86400
print('Checking final line counts: logged =', count, ', should be = ', seconds_per_day)

print()
print('all done!')
print()
print()
