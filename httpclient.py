#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

requestGET = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n'
requestPOST = 'POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\nConnection: close\r\n\r\n'

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        splitData = data.split("\r\n")
        firstLine = splitData[0].split(" ")
        return int(firstLine[1])

    def get_headers(self,data):
        splitData = data.split("\r\n\r\n")
        headersArray = splitData[0].split("\r\n")
        return headersArray[1:]

    def get_body(self, data):
        splitData = data.split("\r\n\r\n")
        return splitData[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        urlParse = urllib.parse.urlparse(url=url)

        port = urlParse.port
        host = urlParse.hostname
        if port == None:    #handling when port == None, use the default http port 80
            port = 80

        #handling args for GET
        if not args:
            args = {}
        args = urllib.parse.urlencode(args)

        self.connect(host, port)

        if urlParse.path != "":
            if args != "":
                self.sendall(requestGET.format(urlParse.path+"?"+args, host))
            else:
                self.sendall(requestGET.format(urlParse.path, host))
        else:
            if args != "":
                self.sendall(requestGET.format("/?"+args, host))
            else:
                self.sendall(requestGET.format("/", host))

        response = self.recvall(self.socket)
        self.close()

        code = self.get_code(response)
        headers = self.get_headers(response)
        body = self.get_body(response)

        print(response)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        urlParse = urllib.parse.urlparse(url=url)

        port = urlParse.port
        host = urlParse.hostname
        if port == None:
            port = 80

        if not args:  #handling when args == None
            args = {}
        args = urllib.parse.urlencode(args)
        
        self.connect(host, port)
        self.sendall(requestPOST.format(urlParse.path, host, len(args))+args)
        response = self.recvall(self.socket)
        self.close()

        code = self.get_code(response)
        headers = self.get_headers(response)
        body = self.get_body(response)

        print(response)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
