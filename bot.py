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

c.on('ready', rdy)
c.on('raw', raw)
c.on('send', send)
c.on('privmsg', privmsg)
c.on('error', error)

c.connect()