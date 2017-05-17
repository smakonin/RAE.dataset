#! /usr/bin/env python3

#
# EMU2_logger.py -- Copyright (C) 2016 Stephen Makonin
#

import os, sys, platform, time, datetime, serial
import xml.etree.ElementTree as et

if platform.system() == 'Darwin':
    dev = '/dev/tty.usbmodem11'
elif platform.system() == 'Linux':
    dev = '/dev/ttyACM0'
else:
    print('ERROR: unknown os type!')
    exit(0)

emu2 = serial.Serial(dev, 115200, timeout=1)
energy = 0
while True:
    msg = emu2.readlines()
    ts = int(time.time())
    dt = datetime.datetime.fromtimestamp(ts)
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
        f = open('/home/pi/REdataset/raw/EMU2_%04d-%02d-%02d.csv' % (dt.year, dt.month, dt.day), 'a')
        f.write(line + '\n')
        f.close()

    elif tree.tag == 'CurrentSummationDelivered':
        energy = int(tree.find('SummationDelivered').text, 16)
        energy -= int(tree.find('SummationReceived').text, 16)
        energy *= int(tree.find('Multiplier').text, 16)
        energy /= int(tree.find('Divisor').text, 16)
        energy = round(energy, int(tree.find('DigitsRight').text, 16))
