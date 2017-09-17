#!/usr/bin/env python3

#
# Eagle200_reader.py -- Copyright (C) 2017 Stephen Makonin
#

import os, sys, platform, time
import xml.etree.ElementTree as et
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        ts = int(time.time())
        dt = datetime.fromtimestamp(ts)
        
        content_len = int(self.headers.get('content-length', 0))
        data = self.rfile.read(content_len)
        msg = data.decode("utf-8")

        print('-------------------------------------------')
        print(msg)
        print('-------------------------------------------')

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


server_address = ('', 80)
httpd = HTTPServer(server_address, RequestHandler)
httpd.serve_forever()

