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

        self.req = QueueServer(self)
        self.update = UpdateInfo(self.req)

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

    def s_auth(self, User, Pass, type, isAdmin = '0'):
        self.send_str(type)
        
        self.send_str(User)
        self.send_str(Pass)
        if (type == 'signUp'):
            self.send_str(isAdmin)

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

    def s_getDetail(self, id):
        self.send_str('getDetail')
        self.send_str(id)
        return self.recv_obj()

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

    def s_editAccount(self, User, Pass, isAdmin):
        self.send_str('editAccount')
        self.send_str(User)
        self.send_str(Pass)
        self.send_str(isAdmin)
        return self.recv_state()
    
    def s_delAccount(self, User):
        self.send_str('delAccount')
        self.send_str(User)
        return self.recv_state()

    def s_accountList(self):
        self.send_str('accountList')
        return self.recv_obj()

    def s_ping(self):
        self.send_str('ping')
        return self.recv_state()

class QueueServer():
    def __init__(self, services):
        self.services = services

        self.request = queue.Queue()
        self.client_thread = None
        self.result = {}

    def run(self):
        while True:
            try:
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
                elif cmd == 'getDetail':
                    res = self.services.s_getDetail(arg)
                elif cmd == 'editDetail':
                    res = self.services.s_editDetail(arg[0], arg[1], arg[2], arg[3], arg[4])
                elif cmd == 'insertDetail':
                    res = self.services.s_insertDetail(arg[0], arg[1], arg[2], arg[3], arg[4], arg[5])
                elif cmd == 'delDetail':
                    res = self.services.s_delDetail(arg)
                elif cmd == 'getHT':
                    res = self.services.s_getHT(arg)
                elif cmd == 'getGoal':
                    res = self.services.s_getGoal(arg)
                elif cmd == 'listAllDate':
                    res = self.services.s_getAllDate(arg)
                elif cmd == 'editAccount':
                    res = self.services.s_editAccount(arg[0], arg[1], arg[2])
                elif cmd == 'delAccount':
                    res = self.services.s_delAccount(arg)
                elif cmd == 'accountList':
                    res = self.services.s_accountList()
                elif cmd == 'signUp':
                    res = self.services.s_auth(arg[0], arg[1], 'signUp', arg[2])
                elif cmd == 'exit':
                    break
                else:
                    res = False
            except:
                self.client_thread = None
                res = False
            finally:
                self.result[id] = res
            
   
    def start(self):
        if self.client_thread is None:
            self.client_thread = threading.Thread(target = self.run, daemon = True)
            self.client_thread.start()

    def stop(self):
        if self.client_thread is not None:
            try:
                self.command('exit')
                self.client_thread.join(5)
            finally:
                self.client_thread = None
                self.result = {}

    def command(self, cmd, arg = ()):
        id = uuid.uuid4().hex
        self.request.put((id, cmd, arg))

        if cmd != 'exit':
            while True:
                if id in self.result:
                    res = self.result[id]
                    self.result.pop(id)
                    return res

class UpdateInfo:
    def __init__(self, req):
        self.req = req

        self.details = {}
        self.remove = []
        self.thread = None
        self.stopped = None
        self.timeout = 1

    def setTimeout(self, time):
        self.timeout = time / 1000

    def addWindows(self, windows, realTime = True):
        self.details[windows] = [realTime, None, None]

    def removeWindows(self, windows):
        self.remove.append(windows)

    def start(self):
        if self.thread is None:
            self.stopped = threading.Event()
            self.thread = threading.Thread(target = self.updatingData, daemon = True)
            self.thread.start()

    def stop(self):
        try:
            self.stopped.set()
            self.thread.join(5)
        finally:
            self.thread = None
            self.details = {}
            self.dateMatch = ''

    def caculateHT(self, details):
        ht_start, ht_len, ot = 45, 0, 0
        for detail in details:
            if detail[3] == 4:
                ht_start = detail[2]
                ht_len = detail[4]
            if detail[3] == 5:
                ot = detail[4]

        return ht_start, ht_len, ot

    def caculateMatch(self, match, details):
        id, timeStamp, team1Name, team2Name= match

        ht_start, ht_len, ot = self.caculateHT(details)
        time, timeInt = self.calcTime(timeStamp, int(ht_start), int(ht_len), int(ot))

        if timeInt != -1:
            score = [0, 0]

            for _match, _id, _time, _code, _team, _player in details:
                if _time > timeInt:
                    break

                if _code == 1:
                    score[_team] += 1

            scoreDisp = str(score[0]) + ' - ' + str(score[1])
        else:
            scoreDisp = '? - ?'
        
        return time, timeInt, scoreDisp

    def calcTime(self, startTime, ht_start, ht_len, ot):
        startTime = datetime.strptime(startTime, '%Y-%m-%d %H:%M')
        
        if datetime.now() < startTime:
            return startTime.strftime('%H:%M'), -1

        time = int ((datetime.now() - startTime).total_seconds() / 60)

        if time < ht_start:
            return str(time) + '\'', time
        elif time < ht_start + ht_len:
            return 'HT', ht_start
        elif time < 90 + ht_len:
            return str(time - ht_len) + '\'', time - ht_len
        elif time < 90 + ht_len + ot:
            return '90\' + ' + str(time - 90 - ht_len) + '\'', time - ht_len
        else:
            return 'FT', time - ht_len

    def updatingData(self):
        try:
            while not self.stopped.wait(self.timeout):
                for ele in self.remove:
                    self.details.pop(ele)
                self.remove = []

                matchDetail = [*self.details]
                matchDetail.remove('main')

                if self.details['main'][0] == False:
                    matches_tuple = self.req.command('listAll')
                else:
                    matches_tuple = self.req.command('listAllDate', self.details['main'][0])

                matches = []
                for match in matches_tuple:
                    id, timeStamp, team1Name, team2Name = match
                    details = self.req.command('getDls', id)

                    time, timeInt, score = self.caculateMatch(match, details)
                    matches.append([id, time, team1Name, score, team2Name])

                    if id in matchDetail:
                        self.details[id][1] = [[id, timeStamp, time, team1Name, team2Name, score, timeInt], None]
                        self.details[id][2] = details
                self.details['main'][1] = matches
                

                for id in matchDetail:
                    if self.details[id][2] is None:
                        details = self.req.command('getDls', id)
                        match = self.req.command('getMatch', id)

                        time, timeInt, score = self.caculateMatch(match[0], details)
                        self.details[id][1] = [[id, timeStamp, time, team1Name, team2Name, score, timeInt], None]
                    else:
                        details = self.details[id][2]
                        self.details[id][2] = None

                    rows = []
                    score = [0, 0]
                    isRealtime = self.details[id][0]
                    timeInt = self.details[id][1][0][6]
                    for _match, _id, _time, _code, _team, _player in details:
                        if isRealtime and _time > timeInt:
                            break

                        if _code == 1:
                            score[_team] += 1

                        codeName = eventCodeToName(_code)
                        if _time > 90:
                            timeDisp = '90\' + ' + str(_time - 90) +'\''
                        else:
                            timeDisp = str(_time) +'\''

                        if _code == 1 or _code == 4 or _code == 5:
                            scoreDisp =  str(score[0]) + ' - ' + str(score[1])
                        else:
                            scoreDisp = ''

                        if _code == 4 or _code == 5:
                            event1 = event2 = codeName
                            player1 = player2 = str(_team) + '\''
                        else:
                            if _team == 0:
                                player1, event1 = _player, codeName
                                player2, event2 = '', ''
                            else:
                                player2, event2 = _player, codeName
                                player1, event1 = '', ''
                        
                        rows.append([_id, timeDisp, player1, event1, scoreDisp, event2, player2])
                    self.details[id][1][1] = rows
        except:
            self.thread = None
            self.details = {}
            self.dateMatch = ''


def eventCodeToName(code):
    if code == 1:
        return 'Goal'
    elif code == 2:
        return 'Yellow card'
    elif code == 3:
        return 'Red card'
    elif code == 4:
        return 'Half-time break'
    elif code == 5:
        return 'Stoppage time'

def eventNameToCode(name):
    if name == 'Goal':
        return '1'
    elif name == 'Yellow card':
        return '2'
    elif name == 'Red card':
        return '3'
    elif name == 'Half-time break':
        return '4'
    elif name == 'Stoppage time':
        return '5'