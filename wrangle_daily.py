#! /usr/bin/env python3

#
# wrangle_daily.py -- Copyright (C) 2016-2017 Stephen Makonin
#

import os, sys

def int32(lsw, msw):
    return msw * 0x10000 + lsw

print()
print('----------------------------------------------------------------------------------------------')
print('Wrangle daily raw data files to the RE dataset format  --  Copyright (C) 2016 Stephen Makonin.')
print('----------------------------------------------------------------------------------------------')
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

meter_count = 8
seconds_per_day = 86400
mains_raw_lines = seconds_per_day // 15
subs_raw_lines = seconds_per_day * 8
mains_final_lines = mains_raw_lines
subs_final_lines = seconds_per_day * submeter_count

print('Checking raw line counts:')
print('\t mains: logged =', len(mains_raw), ', should be =', mains_raw_lines)
print('\t subs: logged =', len(subs_raw), ', should be =', subs_raw_lines)


print('Converting mains data...')
mains_step1 = []
for l in mains_raw:
    l = l.strip()
    l = l.split(',')
    #l = [l[0], -1, -1, -1, -1, l[1], l[2]] # 3 phase
    l = [l[0], -1, -1, -1, l[1], l[2]] # split single phase
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


#final_file =
#'%s.house_%d.circuit_%d.csv'
#'20160214_h1_subs.csv'
#
#'mains.20160214.csv'
#'circuit_%d.20160214.csv'
mains_file = './final/house%d_mains_blk%d.csv' % (house, block)
#mains_heading = 'unix_ts,V_l1,V_l2,V_l3,f,S,St'
mains_heading = 'unix_ts,V_l1,V_l2,f,P,Pt'
f_mains = open(mains_file, 'a')
if header: f_mains.write(mains_heading + '\n')

f_subs = [[]] * submeter_count
subs_heading = 'unix_ts,I,dPF,aPF,P,Q,S,Pt,Qt,St'
for j in range(submeter_count):
    subs_file = './final/house%d_sub%d_blk%d.csv' % (house, j + 1, block)
    f_subs[j] = open(subs_file, 'a')
    if header: f_subs[j].write(subs_heading + '\n')

mains_i = 0
subs_count = 0
offset = 2
prev_ts = 0
for subs_i in range(0, len(subs_step1), meter_count):
    ts = subs_step1[subs_i][0]
    volts_l1 = str(round(subs_step1[subs_i][37 + offset] * 0.1, 1))
    volts_l2 = str(round(subs_step1[subs_i][38 + offset] * 0.1, 1))
    #volts_l3 = str(round(subs_step1[subs_i][39 + offset] * 0.1, 1))
    freq = str(round(subs_step1[subs_i][0 + offset] * 0.1, 1))

    if mains_i < len(mains_step1) and int(mains_step1[mains_i][0]) == ts:
        mains_step1[mains_i][1] = volts_l1
        mains_step1[mains_i][2] = volts_l2
        mains_step1[mains_i][3] = freq
        f_mains.write(','.join(mains_step1[mains_i]) + '\n')
        mains_i += 1

    lines = []
    for i in range(meter_count):
        line = subs_step1[subs_i + i]

        if ord(line[1]) != ord('A') + i:
            print('\t ERROR: meter not equal at line', subs_i + i, ":", line)
            exit(1)

        l1 = [str(ts), str(round(line[34 + offset] * 0.1, 1)), str(round(line[28 + offset] * 0.01, 2)), str(round(line[31 + offset] * 0.01, 2)), str(line[7 + offset]), str(line[16 + offset]), str(line[25 + offset]), str(int32(line[1 + offset], line[2 + offset])), str(int32(line[10 + offset], line[11 + offset])), str(int32(line[19 + offset], line[20 + offset]))]
        l2 = [str(ts), str(round(line[35 + offset] * 0.1, 1)), str(round(line[29 + offset] * 0.01, 2)), str(round(line[32 + offset] * 0.01, 2)), str(line[8 + offset]), str(line[17 + offset]), str(line[26 + offset]), str(int32(line[3 + offset], line[4 + offset])), str(int32(line[12 + offset], line[13 + offset])), str(int32(line[21 + offset], line[22 + offset]))]
        l3 = [str(ts), str(round(line[36 + offset] * 0.1, 1)), str(round(line[30 + offset] * 0.01, 2)), str(round(line[33 + offset] * 0.01, 2)), str(line[9 + offset]), str(line[18 + offset]), str(line[27 + offset]), str(int32(line[5 + offset], line[6 + offset])), str(int32(line[14 + offset], line[15 + offset])), str(int32(line[23 + offset], line[24 + offset]))]

        lines.append(l1)
        lines.append(l2)
        lines.append(l3)
        subs_count += 3

    ts_diff = ts - prev_ts - 1
    if prev_ts > 0 and ts_diff != 0:
        print('\t ERROR:', ts_diff, 'missing readings after ts ', ts)
        for i in range(ts_diff):
            new_ts = prev_ts + i + 1
            mains = ''
            if mains_i < len(mains_step1) and int(mains_step1[mains_i][0]) == new_ts:
                mains_step1[mains_i][1] = ''
                mains_step1[mains_i][2] = ''
                mains_step1[mains_i][3] = ''
                f_mains.write(','.join(mains_step1[mains_i]) + '\n')
                mains_i += 1

            for j in range(submeter_count):
                f_subs[j].write('%d,,,,,,,,,\n' % (new_ts))

    for j in range(submeter_count):
        #f_subs.write('\n'.join([','.join(line) for line in lines]) + '\n')
        f_subs[j].write(','.join(lines[j]) + '\n')
    prev_ts = ts


print('Checking final line counts:')
print('\t mains: logged =', mains_i, ', should be =', mains_final_lines)
print('\t subs: logged =', subs_count, ', should be =', subs_final_lines)


f_mains.close()
for j in range(submeter_count):
    f_subs[j].close()

print()
print('all done!')
print()
print()
