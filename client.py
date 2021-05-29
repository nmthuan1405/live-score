import socket
import pickle
import queue
import threading
import uuid
from datetime import datetime

class Client:
    def __init__(self, serverAddr, port = 1234, delim = b'\x00'):
        self.serverAddr = serverAddr
        self.port = port
        self.delim = delim
        self.isAdmin = None

        self.socket = None
        self.buff = b''

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.serverAddr, self.port))

    def close(self):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        finally:
            self.socket = None

    def recv_until(self, delim = None):
        if delim == None:
            delim = self.delim

        while True:
            pos = self.buff.find(delim)
            if (pos != -1):
                val = self.buff[:pos]
                self.buff = self.buff[pos + len(delim):]

                return val
            else:
                self.buff += self.socket.recv(1024)

    def recv_size(self, size):
        while True:
            sizeBuff = len(self.buff)
            if (sizeBuff >= size):
                val = self.buff[:size]
                self.buff = self.buff[size:]

                return val
            else:
                self.buff += self.socket.recv(1024)

    def recv_str(self, delim = None):
        if delim == None:
            delim = self.delim

        return self.recv_until().decode()

    def recv_obj(self): 
        obj_size = int(self.recv_str())
        obj = self.recv_size(obj_size)

        return pickle.loads(obj)

    def recv_state(self):
        return eval(self.recv_str())

    def send(self, data):
        return self.socket.send(data)

    def send_str(self, string, delim = None):
        if delim == None:
            delim = self.delim

        return self.send(str(string).encode() + delim)
    
    def send_obj(self, object):
        obj = pickle.dumps(object)
        obj_size = len(obj)

        self.send_str(str(obj_size))
        return self.send(obj)

    def send_state(self, state):
        self.send_str(str(state))

    def s_auth(self, User, Pass, type):
        self.send_str(type)
        
        self.send_str(User)
        self.send_str(Pass)
        return self.recv_obj()

    def s_close(self):
        self.send_str('close')
        self.close()

    def s_signOut(self):
        self.send_str('signOut')

    def s_addMatch(self, id, team1Name, team2Name, time):
        self.send_str('addMatch')

        self.send_obj((id, team1Name, team2Name, time))
        return self.recv_state()

    def s_editMatch(self, id, team1Name, team2Name, time):
        self.send_str('editMatch')

        self.send_obj((id, team1Name, team2Name, time))
        return self.recv_state()

    def s_delMatch(self, id):
        self.send_str('delMatch')
        self.send_str(id)
        return self.recv_state()

    def s_getMatch(self):
        self.send_str('getMatch')
        return self.recv_obj()

    def s_getMatchID(self, id):
        self.send_str('getMatchID')
        self.send_str(id)
        return self.recv_obj()

    def s_getDetails(self, match):
        self.send_str('getDls')
        self.send_str(match)
        return self.recv_obj()

    def s_delDetails(self, match):
        self.send_str('delDls')
        self.send_str(match)
        return self.recv_state()

    def s_editDetail(self, id, code, team, player, time):
        self.send_str('editDetail')
        self.send_str(id)
        self.send_str(code)
        self.send_str(team)
        self.send_str(player)
        self.send_str(time)
        return self.recv_state()

    def s_insertDetail(self, id, match, code, team, player, time):
        self.send_str('insertDetail')
        self.send_str(id)
        self.send_str(match)
        self.send_str(code)
        self.send_str(team)
        self.send_str(player)
        self.send_str(time)
        return self.recv_state()

    def s_delDetail(self, id):
        self.send_str('delDetail')
        self.send_str(id)
        return self.recv_state()

    def s_getHT(self, id):
        self.send_str('getHT')
        self.send_str(id)
        return self.recv_obj()

    def s_getGoal(self, id):
        self.send_str('getGoal')
        self.send_str(id)
        return self.recv_obj()

    def s_getAllDate(self, date):
        self.send_str('getAllDate')
        self.send_str(date)
        return self.recv_obj()

class QueueServer():
    def __init__(self, services):
        self.services = services

        self.request = queue.Queue()
        self.client_thread = None
        self.result = {}

    def run(self):
        while True:
            id, cmd, arg = self.request.get()

            if cmd == 'listAll':
                res = self.services.s_getMatch()
            elif cmd == 'addMatch':
                res = self.services.s_addMatch(arg[0], arg[1], arg[2], arg[3])
            elif cmd == 'editMatch':
                res = self.services.s_editMatch(arg[0], arg[1], arg[2], arg[3])
            elif cmd == 'delMatch':
                res = self.services.s_delMatch(arg)
            elif cmd == 'getMatch':
                res = self.services.s_getMatchID(arg)
            elif cmd == 'getDls':
                res = self.services.s_getDetails(arg)
            elif cmd == 'delDls':
                res = self.services.s_delDetails(arg)
            elif cmd == 'editDetail':
                res = self.services.s_editDetail(arg[0], arg[1], arg[2], arg[3], arg[4])
            elif cmd == 'insertDetal':
                res = self.services.s_insertDetail(arg[0], arg[1], arg[2], arg[3], arg[4], arg[5])
            elif cmd == 'delDetail':
                res = self.services.s_delDetail(arg)
            elif cmd == 'getHT':
                res = self.services.s_getHT(arg)
            elif cmd == 'getGoal':
                res = self.services.s_getGoal(arg)
            elif cmd == 'listAllDate':
                res = self.services.s_getAllDate(arg)
            elif cmd == 'exit':
                break
            else:
                res = False

            self.result[id] = res
   
    def start(self):
        if self.client_thread is None:
            self.client_thread = threading.Thread(target = self.run)
            self.client_thread.start()

    def stop(self):
        if self.client_thread is not None:
            self.command('exit')
            self.client_thread.join()
            self.client_thread = None

    def command(self, cmd, arg = ()):
        id = uuid.uuid4().hex
        self.request.put((id, cmd, arg))

        if cmd != 'exit':
            while True:
                if id in self.result:
                    res = self.result[id]
                    self.result.pop(id)
                    return res


def calcTime(startTime, ht_start, ht_len, ot):
    startTime = datetime.strptime(startTime, '%Y-%m-%d %H:%M')
    
    if datetime.now() < startTime:
        return startTime.strftime('%H:%M'), -1
    time = int ((datetime.now() - startTime).seconds / 60)

    if time < ht_start:
        return str(time) + '\'', time
    elif time < ht_start + ht_len:
        return 'HT', ht_start
    elif time < 90 + ht_len:
        return str(time - ht_len) + '\'', time - ht_len
    elif time < 90 + ht_len + ot:
        return str(time - ht_len) + '\' + ' + str(time - 90) + '\'', time - ht_len
    else:
        return 'FT', time - ht_len