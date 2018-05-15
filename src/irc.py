import socket
import functools
import re

# irc4py
# an irc lib for python

class Client:
    def __init__(self, ip, port, username, hostname="irc4py-bot", servername="irc4py", realname="Made with irc4py by ry00001."):
        self.ip = ip
        self.port = port
        self.username = username
        self.hostname = hostname
        self.servername = servername
        self.realname = realname
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer = 1024

        def handle_msg(s, raw):
            split = s.split(' ')
            if s.endswith((f'376 {self.username} :End of MOTD command\r\n', f':{self.username} MODE {self.username} :+i\r\n')) and not 'PRIVMSG' in s.split(' '):
                self.fire('ready')
            elif s.startswith('PING'):
                self.send('PONG ' + s.split(' ')[1][:-2])
            elif split[1] == 'PRIVMSG':
                # oh heck a message
                self.fire('privmsg', split[0][1:], split[2], (" ".join(split[3:]))[1:])

        self.events = {'raw': [handle_msg]}
    
    def connect(self):
        self.socket.connect((self.ip, self.port))
        self.login()
        while True:
            try:
                data = self.socket.recv(self.buffer)
                if not data: continue
                self.fire('raw', data.decode('utf-8'), data)
            except Exception as e:
                self.fire('error', e)

    def disconnect(self, msg = 'Quit By Client', close = True):
        self.send(f'QUIT :{msg}')
        self.socket.shutdown(2)
        self.socket.close()
        if close:
            exit()

    def send(self, s):
        self.fire('send', s)
        self.socket.send(f'{s}\r\n'.encode())

    def login(self):
        self.send(f'USER {self.username} {self.hostname} {self.servername} :{self.realname}')
        self.send(f'NICK {self.username}')

    def privmsg(self, to, msg):
        self.send(f'PRIVMSG {to} :{msg}')

    def on(self, name, event):
        try:
            self.events[name]
        except KeyError:
            self.events[name] = []
        if not self.events[name]:
            self.events[name] = []
        self.events[name].append(event)

    def fire(self, event, *args):
        try:
            self.events[event]
        except KeyError:
            return
        for i in self.events[event]:
            i(*args)
