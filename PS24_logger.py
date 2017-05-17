#! /usr/bin/env python3

#
# PS24_logger.py -- Copyright (C) 2016 Stephen Makonin
#

import os, sys, platform, time, datetime, minimalmodbus

if platform.system() == 'Darwin':
    dev = '/dev/tty.usbmodem41'
elif platform.system() == 'Linux':
    dev = '/dev/ttyACM1'
else:
    print('ERROR: unknown os type!')
    exit(0)

meter_count = 8
meters = []
for i in range(meter_count):
    meters.append(minimalmodbus.Instrument(dev, i + 1))
    meters[i].serial.baudrate = 115200

ts = int(time.time())
while True:
    while ts == int(time.time()):
        time.sleep(0.01)
    ts = int(time.time())
    dt = datetime.datetime.fromtimestamp(ts)

    log_name = '/home/pi/REdataset/raw/PS24_%04d-%02d-%02d.csv' % (dt.year, dt.month, dt.day)

    f = open(log_name, 'a')
    for i in range(meter_count):
        raw = meters[i].read_registers(4021, 43)
        raw = [ts, chr(ord('A') + i)] + raw
        f.write(','.join([str(v) for v in raw]) + '\n')
    f.close()
