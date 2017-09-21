#! /usr/bin/env python3

#
# power_wrangler.py -- Copyright (C) 2016-2017 Stephen Makonin
#

import os, sys, platform, daemon, time, minimalmodbus
from datetime import datetime


if len(sys.argv) != 2:
    print()
    print('USAGE: %s [serial-device - e.g.: /dev/ttyACM0]' % (sys.argv[0]))
    print()
    exit(1)


dev = sys.argv[1]

working_dir = '/RAE'
data_dir = working_dir + '/raw'

meter_count = 8
meters = []


with daemon.DaemonContext():
    for i in range(meter_count):
        meters.append(minimalmodbus.Instrument(dev, i + 1))
        meters[i].serial.baudrate = 115200
        meters[i].read_registers(4021, 4)

    ts = int(time.time())

    while True:
        while ts == int(time.time()):
            time.sleep(0.01)
        ts = int(time.time())
        dt = datetime.fromtimestamp(ts)

        log_name = '%s/SUB_%04d-%02d-%02d.csv' % (data_dir, dt.year, dt.month, dt.day)

        f = open(log_name, 'a')
        for i in range(meter_count):
            raw = meters[i].read_registers(4021, 43)
            raw = [ts, chr(ord('A') + i)] + raw
            f.write(','.join([str(v) for v in raw]) + '\n')

        f.close()
