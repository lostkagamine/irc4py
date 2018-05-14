from src import irc
import json
import sys

cfg = json.load(open('config.json'))

c = irc.Client(cfg['host'], cfg['port'], cfg['username'], cfg['hostname'], cfg['servername'], cfg['realname'])

def rdy():
    for i in cfg['channels']:
        c.send('JOIN ' + i)

cmds = {}
prefix = '!!'

def ping(who, chan, msg):
    c.send(f'PRIVMSG {chan} :Pong!')

def cmd(name, func):
    cmds[name] = func

cmd('ping', ping)

def privmsg(who, chan, msg):
    if not msg.startswith(prefix):
        return
    msg = msg[len(prefix):-2] # get rid of \r\n
    #print(msg.encode())
    split = ' '.split(msg)
    spaces = ' ' in msg
    if spaces:
        name = split[0]
    else:
        name = msg
    try:
        cmds[name]
    except KeyError:
        return
    cmds[name](who, chan, split)

def send(s):
    print(f'>> {s}')

def raw(data, rd):
    if '--raw' in sys.argv:
        print(f'<< {rd}')
    else:
        print(f'<< {data}')

c.on('ready', rdy)
c.on('raw', raw)
c.on('send', send)
c.on('privmsg', privmsg)

try:
    c.connect()
except Exception as e:
    c.disconnect('Exception encountered: ' + str(e))