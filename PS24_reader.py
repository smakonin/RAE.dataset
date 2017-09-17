#! /usr/bin/env python3

#
# PS24_reader.py -- Copyright (C) 2016 Stephen Makonin
#

import os, sys, platform, time, datetime, minimalmodbus

def int32(lsw, msw):
    return msw * 0x10000 + lsw

print()
print('Read your DENT PowerScout 24 meter:')
print()

if platform.system() == 'Darwin':
    dev = '/dev/tty.usbmodem41'
elif platform.system() == 'Linux':
    dev = '/dev/ttyACM0'
else:
    print('ERROR: unknown os type!')
    exit(0)
    
meter_count = 8
meters = [None] * meter_count
print('Connecting to meter via USB serial', end='')
while True:
    print('.', end='')
    try:
        for i in range(meter_count):
            meters[i] = minimalmodbus.Instrument(dev, i + 1)
            meters[i].serial.baudrate = 115200
            meters[i].read_registers(4021, 4)
    except:
        #time.sleep(0.1)
        continue
    break
print('Done!')


ts = int(time.time())
dt = datetime.datetime.fromtimestamp(ts)

data = []
for i in range(meter_count):
    data.append(meters[i].read_registers(4021, 43))    



print()
print('Time Since Reset / Data Tick Counter: %d/%d' % (int32(data[0][40], data[0][41]), data[0][42]))

print()
print('L1 Voltage..... %5.1f' % (round(data[0][37] * 0.1, 1)))
print('L2 Voltage..... %5.1f' % (round(data[0][38] * 0.1, 1)))
print('L3 Voltage..... %5.1f' % (round(data[0][39] * 0.1, 1)))
print('Frequency...... %5.1f' % (round(data[0][0] * 0.1, 1)))

print()
print(' Measurement Type      Meter A   Meter B   Meter C   Meter D   Meter E   Meter F   Meter G   Meter H ')
print('--------------------- --------- --------- --------- --------- --------- --------- --------- ---------')
print('CT1: Current......... %8.1f  %8.1f  %8.1f  %8.1f  %8.1f  %8.1f  %8.1f  %8.1f' % tuple([round(d[34] * 0.1, 1) for d in data]))
print('     Power Factor.... %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f' % tuple([round(d[28] * 0.01, 2) for d in data]))
print('     Apparent PF..... %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f' % tuple([round(d[31] * 0.01, 2) for d in data]))
print('     Power Real/True. %6d    %6d    %6d    %6d    %6d    %6d    %6d    %6d' % tuple([d[7] for d in data]))
print('           Reactive.. %6d    %6d    %6d    %6d    %6d    %6d    %6d    %6d' % tuple([d[16] for d in data]))
print('           Apparent.. %6d    %6d    %6d    %6d    %6d    %6d    %6d    %6d' % tuple([d[25] for d in data]))
print()
print('CT2: Current......... %8.1f  %8.1f  %8.1f  %8.1f  %8.1f  %8.1f  %8.1f  %8.1f' % tuple([round(d[35] * 0.1, 1) for d in data]))
print('     Power Factor.... %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f' % tuple([round(d[29] * 0.01, 2) for d in data]))
print('     Apparent PF..... %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f' % tuple([round(d[32] * 0.01, 2) for d in data]))
print('     Power Real/True. %6d    %6d    %6d    %6d    %6d    %6d    %6d    %6d' % tuple([d[8] for d in data]))
print('           Reactive.. %6d    %6d    %6d    %6d    %6d    %6d    %6d    %6d' % tuple([d[17] for d in data]))
print('           Apparent.. %6d    %6d    %6d    %6d    %6d    %6d    %6d    %6d' % tuple([d[26] for d in data]))
print()
print('CT3: Current......... %8.1f  %8.1f  %8.1f  %8.1f  %8.1f  %8.1f  %8.1f  %8.1f' % tuple([round(d[36] * 0.1, 1) for d in data]))
print('     Power Factor.... %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f' % tuple([round(d[30] * 0.01, 2) for d in data]))
print('     Apparent PF..... %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f' % tuple([round(d[33] * 0.01, 2) for d in data]))
print('     Power Real/True. %6d    %6d    %6d    %6d    %6d    %6d    %6d    %6d' % tuple([d[9] for d in data]))
print('           Reactive.. %6d    %6d    %6d    %6d    %6d    %6d    %6d    %6d' % tuple([d[18] for d in data]))
print('           Apparent.. %6d    %6d    %6d    %6d    %6d    %6d    %6d    %6d' % tuple([d[27] for d in data]))
print()

for i in range(meter_count):
    meters[i].serial.close()

