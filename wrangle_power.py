#! /usr/bin/env python3

#
# wrangle_power.py -- Copyright (C) 2016-2017 Stephen Makonin
#

import os, sys

def int32(lsw, msw):
    return msw * 0x10000 + lsw

print()
print('----------------------------------------------------------------------------------------------')
print('Wrangle power raw data files to store only power data  --  Copyright (C) 2017 Stephen Makonin.')
print('----------------------------------------------------------------------------------------------')
print()

if len(sys.argv) != 7:
    print()
    print('USAGE: %s [house #] [block #] [header|no-header] [date, e.g., 2016-02-07] [mains: 1,2 OR calc] [sub-meters]' % (sys.argv[0]))
    print()
    exit(1)

house = int(sys.argv[1])
block = int(sys.argv[2])
header = True if sys.argv[3] == 'header' else False
date = sys.argv[4]
mains = sys.argv[5]
calc_mains = True if mains == "calc" else False
mains = [int(i)-1 for i in mains.split(',')] if not calc_mains else []
submeter_count = int(sys.argv[6])

raw_dir = './raw/house%d' % (house)
ihd_file = '%s/IHD_%s.csv' % (raw_dir, date)
subs_file = '%s/SUB_%s.csv' % (raw_dir, date)

print('Checking for existance of file: %s' % (ihd_file))
if not os.path.isfile(ihd_file):
    print('\t ERROR: file does not exist!')
    exit(1)

print('\t Loading data...')
f_ihd = open(ihd_file, 'r')
ihd_raw = list(f_ihd)
f_ihd.close()

print('Checking for existance of file: %s' % (subs_file))
if not os.path.isfile(subs_file):
    print('\t ERROR: file does not exist!')
    exit(1)

print('\t Loading data...')
f_subs = open(subs_file, 'r')
subs_raw = list(f_subs)
f_subs.close()

print('Converting ihd data...')
ihd_step1 = []
for l in ihd_raw:
    l = l.strip()
    l = l.split(',')
    ihd_step1.append(l)

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
final_file = './final/house%d_power_blk%d.csv' % (house, block)

heading = 'unix_ts,ihd,mains,' + ','.join(['sub' + str(i) for i in range(1, submeter_count+1)])

f = open(final_file, 'a')
if header: f.write(heading + '\n')

ihd_i = 0
count = 0
prev_ts = 0
for subs_i in range(0, len(subs_step1), meter_count):
    l = []

    ts = subs_step1[subs_i][0]
    l.append(str(ts))

    ihd = ''
    if ihd_i < len(ihd_step1) and int(ihd_step1[ihd_i][0]) == ts:
        ihd = str(int(float(ihd_step1[ihd_i][1]) * 1000))
        ihd_i += 1
    l.append(ihd)
    l.append(0)

    for i in range(meter_count):
        line = subs_step1[subs_i + i]

        if ord(line[1]) != ord('A') + i:
            print('\t ERROR: meter not equal at line', subs_i + i, ":", line)
            exit(1)

        l += [str(line[7 + 2]), str(line[8 + 2]), str(line[9 + 2])]

    ts_diff = ts - prev_ts - 1
    if prev_ts > 0 and ts_diff != 0:
        print('\t ERROR:', ts_diff, 'missing readings after ts ', ts)
        for i in range(ts_diff):
            new_ts = prev_ts + i + 1
            ihd = ''
            if ihd_i < len(ihd_step1) and int(ihd_step1[ihd_i][0]) == new_ts:
                ihd = str(int(float(ihd_step1[ihd_i][1]) * 1000))
                ihd_i += 1
            f.write('%d,%s%s\n' % (new_ts, ihd, ',' * (submeter_count+1)))

    if calc_mains:
        l[2] = sum([int(i) for i in l[3:]])
    else:
        for i in mains:
            l[2] += int(l[i+3])
    l[2] = str(l[2])

    f.write(','.join(l[:submeter_count+3]) + '\n')
    prev_ts = ts
    count += 1

f.close()

seconds_per_day = 86400
print('Checking final line counts: logged =', count, ', should be = ', seconds_per_day)

print()
print('all done!')
print()
print()
