from src import irc
import json
import sys

cfg = json.load(open('config.json'))

try:
    password = cfg['password']
except KeyError:
    password = None

c = irc.Client(cfg['host'], cfg['port'], cfg['username'], password=password, hostname=cfg['hostname'], servername=cfg['servername'], realname=cfg['realname'])

cmds = {}
prefix = '!!'

def ping(who, chan, msg):
    if chan == c.username:
        chan = who.split('!')[0]
    c.privmsg(chan, 'Pong!')

def crash(who, chan, msg):
    if who == cfg['owner']:
        raise Exception()

def stop(who, chan, msg):
    if who == cfg['owner']:
        c.disconnect()

def cmd(name, func):
    cmds[name] = func

cmd('ping', ping)
cmd('crash', crash)
cmd('stop', stop)

def privmsg(who, chan, msg):
    print(f'privmsg {chan}: {msg}')
    if not msg.startswith(prefix):
        return
    if who.split('!')[0] == c.username:
        return # prevent it from responding to itself
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
    forbidden = ['JOIN', 'QUIT']
    for i in forbidden:
        if i in data:
            return
    if '--raw' in sys.argv:
        print(f'<< {rd}')
    else:
        print(f'<< {data}')

def error(e):
    if type(e) == KeyboardInterrupt:
        c.disconnect('Quit by owner')
    else:
        c.privmsg(cfg['home-channel'], f'Exception encountered: {type(e).__name__}: {e}')
        c.disconnect()

def rdy():
    print('Ready')
    for i in cfg['channels']:
        c.send(f'JOIN {i}')

c.on('raw', raw)
c.on('send', send)
c.on('privmsg', privmsg)
c.on('error', error)
c.on('ready', rdy)

c.connect()