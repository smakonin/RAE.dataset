#!/usr/bin/env python3

#
# Eagle200_logger.py -- Copyright (C) 2017 Stephen Makonin
#

import os, sys, platform, daemon, time
import xml.etree.ElementTree as et
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


working_dir = '/RAE'
data_dir = working_dir + '/raw'

energy = 0


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global energy

        ts = int(time.time())
        dt = datetime.fromtimestamp(ts)

        content_len = int(self.headers.get('content-length', 0))
        data = self.rfile.read(content_len)
        msg = data.decode("utf-8")

        try:
            root = et.fromstring(msg)
        except:
            self.send_response(400)
            self.end_headers()
            return

        for child in root:
            if child.tag == 'InstantaneousDemand':
                power = int(child.find('Demand').text, 16)
                power *= int(child.find('Multiplier').text, 16)
                power /= int(child.find('Divisor').text, 16)
                power = round(power, int(child.find('DigitsRight').text, 16))

                line = '%d,%.3f,%.1f' % (ts, power, energy)
                log_name = '%s/IHD_%04d-%02d-%02d.csv' % (data_dir, dt.year, dt.month, dt.day)
                f = open(log_name, 'a')
                f.write(line + '\n')
                f.close()

            elif child.tag == 'CurrentSummation':
                energy = int(child.find('SummationDelivered').text, 16)
                energy -= int(child.find('SummationReceived').text, 16)
                energy *= int(child.find('Multiplier').text, 16)
                energy /= int(child.find('Divisor').text, 16)
                energy = round(energy, int(child.find('DigitsRight').text, 16))

        self.send_response(200)
        self.end_headers()
        return

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        message = 'RAE Server'
        self.wfile.write(bytes(message, "utf8"))
        return


with daemon.DaemonContext():
    server_address = ('', 80)
    httpd = HTTPServer(server_address, RequestHandler)
    httpd.serve_forever()

