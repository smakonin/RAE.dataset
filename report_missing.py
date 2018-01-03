#! /usr/bin/env python3

#
# report_missing.py -- Copyright (C) 2016-2017 Stephen Makonin
#

import os, sys

def int32(lsw, msw):
    return msw * 0x10000 + lsw

if len(sys.argv) != 4:
    print()
    print('USAGE: %s [house #] [house] [date, e.g., 2016-02-07] [sub-meters]' % (sys.argv[0]))
    print()
    exit(1)

house = int(sys.argv[1])
date = sys.argv[2]
submeter_count = int(sys.argv[3])

raw_dir = './raw/house%d' % (house)
subs_file = '%s/SUB_%s.csv' % (raw_dir, date)

if not os.path.isfile(subs_file):
    print('\t ERROR:', subs_file, 'file does not exist!')
    exit(1)

f_subs = open(subs_file, 'r')
subs_raw = list(f_subs)
f_subs.close()

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
prev_ts = 0
for subs_i in range(0, len(subs_step1), meter_count):
    ts = subs_step1[subs_i][0]
    ts_diff = ts - prev_ts - 1
    if prev_ts > 0 and ts_diff != 0:
        print('\t ERROR:', ts_diff, 'missing readings after ts ', ts)
    prev_ts = ts
