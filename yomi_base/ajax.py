# -*- coding: utf-8 -*-

# Copyright (C) 2016  Alex Yatskov <alex@foosoft.net>
# Author: Alex Yatskov <alex@foosoft.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import json
import select
import socket


class AjaxRequest:
    def __init__(self, headers, body):
        self.headers = headers
        self.body = body


class AjaxClient:
    def __init__(self, sock, callback):
        self.sock = sock
        self.callback = callback
        self.readBuff = ''
        self.readBuff = ''


    def advance(self, recvSize=1):
        if self.sock is None:
            return False

        rlist, wlist = select.select([self.sock], [self.sock], [], 0)[:2]

        if rlist:
            msg = self.sock.recv(recvSize)
            if not msg:
                self.close()
                return False

            self.readBuff += msg

            req, length = self.parseRequest(self.readBuff)
            if req is not None:
                self.readBuff = self.readBuff[length:]
                self.readBuff += self.callback(req)

        if wlist and self.readBuff:
            length = self.sock.send(self.readBuff)
            self.readBuff = self.readBuff[length:]
            if not self.readBuff:
                self.close()
                return False

        return True


    def close(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None

        self.readBuff = ''
        self.readBuff = ''


    def parseRequest(self, data):
        parts = data.split('\r\n\r\n', 1)
        if len(parts) == 1:
            return None, 0

        headers = {}
        for line in parts[0].split('\r\n'):
            pair = line.split(': ')
            headers[pair[0]] = pair[1] if len(pair) > 1 else None

        headerLength = len(parts[0]) + 4
        bodyLength = int(headers['Content-Length'])
        totalLength = headerLength + bodyLength

        if totalLength > len(data):
            return None, 0

        body = data[headerLength : totalLength]
        return AjaxRequest(headers, body), totalLength


class AjaxServer:
    def __init__(self, callback):
        self.callback = callback
        self.clients = []
        self.sock = None


    def advance(self):
        if self.sock is not None:
            self.acceptClients()
            self.advanceClients()


    def acceptClients(self):
        rlist = select.select([self.sock], [], [], 0)[0]
        if not rlist:
            return

        clientSock = self.sock.accept()[0]
        if clientSock is not None:
            clientSock.setblocking(False)
            self.clients.append(AjaxClient(clientSock, self.callbackWrapper))


    def advanceClients(self):
        self.clients = filter(lambda c: c.advance(), self.clients)


    def listen(self, address='127.0.0.1', port=8888, backlog=5):
        self.close()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(False)
        self.sock.bind((address, port))
        self.sock.listen(backlog)


    def callbackWrapper(self, req):
        body = json.dumps(self.callback(json.loads(req.body)))
        resp = ''

        headers = {
            'HTTP/1.1 200 OK': None,
            'Content-Type': 'application/json',
            'Content-Length': str(len(body)),
            'Access-Control-Allow-Origin': '*'
        }

        for key, value in headers.items():
            if value is None:
                resp += '{}\r\n'.format(key)
            else:
                resp += '{}: {}\r\n'.format(key, value)

        resp += '\r\n'
        resp += body

        return resp


    def close(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None

        for client in self.clients:
            client.close()

        self.clients = []
