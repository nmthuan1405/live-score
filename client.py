import socket
import pickle

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
        return bool(self.recv_str())

    def send(self, data):
        return self.socket.send(data)

    def send_str(self, string, delim = None):
        if delim == None:
            delim = self.delim

        return self.send(string.encode() + delim)
    
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