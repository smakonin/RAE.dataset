#! /usr/bin/env python3

#
# EMU2_reader.py -- Copyright (C) 2016 Stephen Makonin
#

import os, sys, platform, time, datetime, serial
import xml.etree.ElementTree as et

print()
print('Read your Rainforest EMU2 device:')
print()

if platform.system() == 'Darwin':
    dev = '/dev/tty.usbmodem11'
elif platform.system() == 'Linux':
    dev = '/dev/ttyACM0'
else:
    print('ERROR: unknown os type!')
    exit(0)

emu2 = serial.Serial(dev, 115200, timeout=1)

try:
    delivered_ts = demand_ts = 0
    while True:
        msg = emu2.readlines()
        if msg == [] or msg[0].decode()[0] != '<':
            continue     
        
        msg = ''.join([line.decode() for line in msg])
        
        try:
            tree = et.fromstring(msg)
        except:
            continue
                    
        if tree.tag == 'InstantaneousDemand':
            ts = int(tree.find('TimeStamp').text, 16)
            diff = ts - demand_ts
            demand_ts = ts
            
            power = int(tree.find('Demand').text, 16)
            power *= int(tree.find('Multiplier').text, 16)
            power /= int(tree.find('Divisor').text, 16)
            power = round(power, int(tree.find('DigitsRight').text, 16))
            print('Message:', tree.tag, '- Apparent Power = ', power, 'kW', '(delay', diff, 's).')
        elif tree.tag == 'CurrentSummationDelivered':
            ts = int(tree.find('TimeStamp').text, 16)
            diff = ts - delivered_ts
            delivered_ts = ts

            energy = int(tree.find('SummationDelivered').text, 16)
            energy -= int(tree.find('SummationReceived').text, 16)
            energy *= int(tree.find('Multiplier').text, 16)
            energy /= int(tree.find('Divisor').text, 16)
            energy = round(energy, int(tree.find('DigitsRight').text, 16))
            print('Message:', tree.tag, '- Net Apparent Energy = ', energy, 'kWh', '(delay', diff, 's).')
        else:
            print()
            print('Message:', tree.tag)
            for child in tree:
                value = int(child.text, 16) if child.text[:2] == '0x' else child.text
                print('\t', child.tag, '=', value)
            print()
            
except KeyboardInterrupt:
    print()
    print('User break signaled!')
    print()
    emu2.close()    
    sys.exit(0)
