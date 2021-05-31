import socket
import pickle
from sqlite3.dbapi2 import sqlite_version_info
import threading
from tkinter import INSERT
import database

class Server:
    def __init__(self, log, maxClient, port = 1234):
        self.port = port
        self.clients = []
        self.log = log
        self.clientCount = [0, maxClient]


        self.socket = None
        self.server_thread = None
        self.db = None

    def start(self):
        self.writeLog('START SERVER')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', self.port))
        self.socket.listen()

        self.server_thread = threading.Thread(target = self.addClient)
        self.server_thread.start()
        self.writeLog('Start add client thread')
        
        self.db = database.Database()
        self.db.start()
        self.writeLog('Start database thread')

    def stop(self):
        self.writeLog('STOP SERVER')

        try:
            for client in self.clients:
                if not client.isClosed():
                    client.close()
        except:
            pass

        server = self.socket
        self.socket = None

        try:
            # server.shutdown(socket.SHUT_RDWR)
            server.close()
        finally:
            self.server_thread.join()
            self.db.stop()
            self.writeLog('Exit database thread')

    def countClient(self):
        count = 0
        for client in self.clients:
                if not client.isClosed():
                    count += 1
        return count

    def addClient(self):
        while True:
            try:
                conn, addr = self.socket.accept()

                if self.clientCount[0] >= self.clientCount[1]:
                    conn.close()
                    self.writeLog('Number of client(s) is maximum')
                else:
                    client = Client(conn, addr, self.db, self.log, self.clientCount)
                    self.clients.append(client)
                    client.start()
                    
            except:
                if self.socket == None:
                    self.writeLog('Server stopped. Exit thread')
                else:
                    self.socket = None
                    self.writeLog('Server have unexpected error. Exit thread')
                    self.db.stop()
                    self.writeLog('Exit database thread')
                break

    def writeLog(self, data):
        self.log.put(data)



class Client:
    def __init__(self, socket, addr, db, log, clientCount, delim = b'\x00'):
        self.addr = addr
        self.log = log
        self.delim = delim
        self.isAdmin = None

        self.socket = socket
        self.buff = b''
        self.client_thread = None
        self.db = db
        self.clientCount = clientCount
        self.clientCount[0] += 1

    def start(self):
        self.writeLog('START CLIENT')
        self.client_thread = threading.Thread(target = self.services)
        self.client_thread.start()

    def close(self):
        self.writeLog('STOP CLIENT')
        client = self.socket
        self.socket = None

        try:
            client.shutdown(socket.SHUT_RDWR)
            client.close()
        finally:
            try:
                self.client_thread.join()
            except:
                pass

    def services(self):
        while True:

            try:
                flag = self.recv_str()
                self.writeLog(f'Received: {flag}')

                if flag == 'close':
                    self.close()
                elif flag == 'signUp':
                    self.c_signUp()
                elif flag == 'ping':
                    self.send_state(True)

                else:
                    if self.isAdmin is None:
                        if flag == 'signIn':
                            self.c_signIn()
                    else:
                        if flag == 'signOut':
                            self.c_signOut()
                        elif flag == 'getMatch':
                            self.c_getMatch()
                        elif flag == 'getMatchID':
                            self.c_getMatchID()
                        elif flag == 'getDls':
                            self.c_getDetails()
                        elif flag == 'getHT':
                            self.c_getHT()
                        elif flag == 'getGoal':
                            self.c_getGoal()
                        elif flag == 'getAllDate':
                            self.c_getAllDate()

                        if self.isAdmin:
                            if flag == 'addMatch':
                                self.c_addMatch()
                            elif flag == 'editMatch':
                                self.c_editMatch()
                            elif flag == 'delMatch':
                                self.c_delMatch()
                            elif flag == 'getDetail':
                                self.c_getDetail()
                            elif flag == 'editDetail':
                                self.c_editDetail()
                            elif flag == 'insertDetail':
                                self.c_insertDetail()
                            elif flag == 'delDetail':
                                self.c_delDetail()
                            elif flag == 'editAccount':
                                self.c_editAccount()
                            elif flag == 'delAccount':
                                self.c_delAccount()
                            elif flag == 'accountList':
                                self.c_accountList()

            except:
                if self.isClosed():
                    self.writeLog('Client closed. Exit thread')
                else:
                    self.socket = None
                    self.writeLog('Client have unexpected error. Exit thread')
                self.clientCount -= 1
                break
            

    def isClosed(self):
        return self.socket is None
    
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

    def writeLog(self, data):
        self.log.put(f'({self.addr[0]}, {self.addr[1]}): ' +  data)

    def c_signIn(self):
        User = self.recv_str()
        Pass = self.recv_str()

        self.isAdmin = self.db.checkAccount(User, Pass)
        self.send_obj(self.isAdmin)

        self.writeLog(f'SIGN IN. Admin: {self.isAdmin}')

    def c_signUp(self):
        User = self.recv_str()
        Pass = self.recv_str()
        isAdmin = self.recv_str()

        state = self.db.insertAccount(User, Pass, isAdmin)
        self.send_obj(state)

        self.writeLog(f'SIGN UP. Sucess: {state}')

    def c_signOut(self):
        self.isAdmin = None
        self.writeLog('SIGN OUT')

    def c_addMatch(self):
        id, team1Name, team2Name, time = self.recv_obj()

        self.send_state(self.db.insertMatch(id, team1Name, team2Name, time))

        self.writeLog(f'Add match. ID: {id}')

    def c_editMatch(self):
        id, team1Name, team2Name, time = self.recv_obj()
        self.send_state(self.db.editMatch(id, team1Name, team2Name, time))

        self.writeLog(f'Edit match. ID: {id}')

    def c_delMatch(self):
        id = self.recv_str()
        self.send_state(self.db.deleteMatch(id))

        self.writeLog(f'Delete match. ID: {id}')

    def c_getMatch(self):
        self.send_obj(self.db.getMatch())

    def c_getMatchID(self):
        id = self.recv_str()
        self.send_obj(self.db.getMatchID(id))

    def c_getDetails(self):
        match = self.recv_str()
        self.send_obj(self.db.getDetails(match))

    def c_getDetail(self):
        id = self.recv_str()
        self.send_obj(self.db.getDetail(id))

    def c_insertDetail(self):
        id = self.recv_str()
        match = self.recv_str()
        code = self.recv_str()
        team = self.recv_str()
        player = self.recv_str()
        time = self.recv_str()

        self.send_state(self.db.insertDetail(match, id, code, time, team, player))

    def c_editDetail(self):
        id = self.recv_str()
        code = self.recv_str()
        team = self.recv_str()
        player = self.recv_str()
        time = self.recv_str()

        self.send_state(self.db.editDetail(id, code, time, team, player))

    def c_delDetail(self):
        id = self.recv_str()

        self.send_state(self.db.delDetail(id))

    def c_getHT(self):
        id = self.recv_str()
        self.send_obj(self.db.getHT(id))

    def c_getGoal(self):
        id = self.recv_str()
        self.send_obj(self.db.getGoal(id))

    def c_getAllDate(self):
        date = self.recv_str()
        self.send_obj(self.db.getMatchDate(date))

    def c_editAccount(self):
        User = self.recv_str()
        Pass = self.recv_str()
        isAdmin = self.recv_str()
        self.send_state(self.db.editAccount(User, Pass, isAdmin))

    def c_delAccount(self):
        User = self.recv_str()
        self.send_state(self.db.delAccount(User))

    def c_accountList(self):
        self.send_obj(self.db.accountList())