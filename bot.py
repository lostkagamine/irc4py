from src import irc
import json

cfg = json.load(open('config.json'))

c = irc.Client(cfg['host'], cfg['port'], cfg['username'], cfg['hostname'], cfg['servername'], cfg['realname'])

def rdy():
    print('o no we ready bois.')
    c.send('JOIN #general')

def privmsg(who, chan, msg):
    print(f'{who} ({chan}): {msg}')
    c.send(f'PRIVMSG {who.split("!")[0]} :{msg}')

def send(s):
    print(f'>> {s}')

def raw(data, rd):
    print(f'<< {data}')

c.on('ready', rdy)
c.on('raw', raw)
c.on('send', send)
c.on('privmsg', privmsg)

print(c.events)

c.connect()