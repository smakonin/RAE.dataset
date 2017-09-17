#! /usr/bin/env python3

#
# EMU2_logger.py -- Copyright (C) 2016-2017 Stephen Makonin
#

import os, sys, platform, daemon, time, serial
from datetime import datetime
import xml.etree.ElementTree as et


if len(sys.argv) != 2:
    print()
    print('USAGE: %s [serial-device - e.g.: /dev/ttyACM0]' % (sys.argv[0]))
    print()
    exit(1)


dev = sys.argv[1]

working_dir = '/RAE'
data_dir = working_dir + '/raw'


with daemon.DaemonContext():
    emu2 = serial.Serial(dev, 115200, timeout=1)
    energy = 0

    while True:
        msg = emu2.readlines()
        ts = int(time.time())
        dt = datetime.fromtimestamp(ts)
        if msg == [] or msg[0].decode()[0] != '<':
            continue

        msg = ''.join([line.decode() for line in msg])

        try:
            tree = et.fromstring(msg)
        except:
            continue

        if tree.tag == 'InstantaneousDemand':
            power = int(tree.find('Demand').text, 16)
            power *= int(tree.find('Multiplier').text, 16)
            power /= int(tree.find('Divisor').text, 16)
            power = round(power, int(tree.find('DigitsRight').text, 16))

            line = '%d,%.3f,%.1f' % (ts, power, energy)
            f = open('%s/IHD_%04d-%02d-%02d.csv' % (data_dir, dt.year, dt.month, dt.day), 'a')
            f.write(line + '\n')
            f.close()

        elif tree.tag == 'CurrentSummationDelivered':
            energy = int(tree.find('SummationDelivered').text, 16)
            energy -= int(tree.find('SummationReceived').text, 16)
            energy *= int(tree.find('Multiplier').text, 16)
            energy /= int(tree.find('Divisor').text, 16)
            energy = round(energy, int(tree.find('DigitsRight').text, 16))
