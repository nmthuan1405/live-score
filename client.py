import socket
import pickle
import queue
import threading
import uuid
from datetime import datetime
import time as tm

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
        self.dateMatch = ''
        self.thread = None
        self.timeout = 1

    def setTimeout(self, time):
        self.timeout = time / 1000

    def setDate(self, date):
        self.dateMatch = str(date)

    def addWindows(self, windows, full = True):
        self.details[windows] = [full, None]

    def removeWindows(self, windows):
        self.details.pop(windows)

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target = self.updatingData)
            self.thread.start()

    def stop(self):
        self.details.pop('main')
        self.thread.join()

        self.thread = None
        self.details = {}
        self.dateMatch = ''

    def updatingData(self):
        while True:
            matches = []
            check = [*self.details]
            if 'main' in check:
                check.remove('main')
            else:
                break

            if self.dateMatch == '':
                matches_tuple = self.req.command('listAll')
            else:
                matches_tuple = self.req.command('listAllDate', self.dateMatch)

            if matches_tuple != []:
                for element in matches_tuple:
                    haveDetail = element[0] in check
                    if haveDetail:
                        details = self.req.command('getDls', element[0])

                    if element[6] == 1: 
                        time = 'FT'
                        score = str(element[4]) + ' - ' + str(element[5])
                    
                    else:
                        if haveDetail:
                            ht_start, ht_len = 45, 0
                            for detail in details:
                                if detail[3] == 4:
                                    ht_start = detail[2]
                                    ht_len = detail[4]
                                    break

                        else:
                            ht = self.req.command('getHT', element[0])
                            if not ht:
                                ht_start, ht_len = 45, 0
                            else:
                                ht_start, ht_len = ht[0]

                        time, timeInt = calcTime(element[1], int(ht_start), int(ht_len), 0)
                        if timeInt != -1:
                            if haveDetail:
                                rows = []
                                score = [0, 0]
                                for detail in details:
                                    id = detail[1]
                                    time = str(detail[2]) + '\''
                                    event = eventCodeToName(detail[3])
                                    player = detail[5]
                                    
                                    if detail[3] == 1:
                                        score[detail[4]] += 1
                                    
                                    if detail[3] != 4 and detail[3] != 5:
                                        if detail[4] == 0:
                                            player1, event1 = player, event
                                            player2, event2 = '', ''
                                        else:
                                            player2, event2 = player, event
                                            player1, event1 = '', ''
                                    else:
                                        event1 = event2 = event
                                        player1 = player2 = ''

                                    scoreDisp = str(score[0]) + ' - ' + str(score[1])
                                    rows.append([id, time, player1, event1, scoreDisp, event2, player2])
                                
                                # for detail in details:
                                #     if detail[2] <= timeInt:
                                #         if detail[3] == 1:
                                #             score[detail[4]] += 1
                                #     else:
                                #         break
                            else:
                                goals = self.req.command('getGoal', element[0])
                                score = [0, 0]
                                if goals:
                                    for goal in goals:
                                        if goal[0] <= timeInt:
                                            score[goal[1]] += 1
                                        else:
                                            break

                            scoreDisp = str(score[0]) + ' - ' + str(score[1])
                        else:
                            scoreDisp = '? - ?'

                    if haveDetail:
                        self.details[element[0]] = [list(element)[0:4] + [scoreDisp, time], rows]
                    matches.append([element[0], time, element[2], scoreDisp, element[3]])
            
            self.details['main'] = matches
            tm.sleep(self.timeout)


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