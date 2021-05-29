import sqlite3
import uuid
import os
import queue
import threading

class Database:
    def __init__(self, dbName = 'database.db'):
        isExists = os.path.isfile(dbName)

        self.con = sqlite3.connect(dbName, check_same_thread=False)
        self.cur = self.con.cursor()

        if not isExists:
            self.createTable()

        self.request = queue.Queue()
        self.result = {}
        self.db_thread = None
    
    def execute(self, cmd, val = ()):
        self.cur.execute(cmd, val)

    def query(self, cmd, val = ()):
        self.execute(cmd, val)
        return self.cur.fetchall()

    def update(self, cmd, val = ()):
        self.execute(cmd, val)
        self.con.commit()

    def updates(self, rows):
        try:
            for row in rows:
                cmd, val = row
                self.execute(cmd, val)
        except:
            self.con.rollback()
            raise Exception
        else:
            self.con.commit()

    def createTable(self):
        self.execute("CREATE TABLE IF NOT EXISTS auth(user text, pass text, isAdmin int, PRIMARY KEY (user))")
        self.execute("CREATE TABLE IF NOT EXISTS match(id text, time text, team1 text, team2 text, score text, isDone int, PRIMARY KEY (id))")
        self.execute("CREATE TABLE IF NOT EXISTS detail(match text, id text, time int, code int, team int, player text, PRIMARY KEY (id), FOREIGN KEY (match) REFERENCES match(id))")

        self.update("INSERT INTO auth VALUES ('admin', 'admin', 1)")

    def insertAccount(self, User, Pass, isAdmin = False):
        return self.command('update', "INSERT INTO auth VALUES (?, ?, ?)", (User, Pass, int(isAdmin)))

    def checkAccount(self, User, Pass):
        data = self.command('query', "SELECT * FROM auth WHERE user = ? AND pass = ?", (User, Pass))

        if (len(data) != 0):
            return bool(data[0][2])
        return None

    def insertMatch(self, id, team1Name, team2Name, time):
        return self.command('updates', [("INSERT INTO match VALUES (?, ?, ?, ?, '', 0)", (id, time, team1Name, team2Name)),
                                        ("INSERT INTO detail VALUES (?, ?, '45', 4, '15', '')", (id, uuid.uuid4().hex))])

    def getMatch(self):
        return self.command('query', 'SELECT * FROM match ORDER BY datetime(time)')

    def getMatchID(self, id):
        return self.command('query', "SELECT * FROM match WHERE id = ?", (id,))

    def editMatch(self, id, team1Name, team2Name, time):
        return self.command('update', "UPDATE match SET team1 = ?, team2 = ?, time = ?, isDone = 0 WHERE id = ?", (team1Name, team2Name, time, id)) 

    def deleteMatch(self, id):
        return self.command('updates', [("DELETE FROM detail WHERE match = ?", (id,)), ("DELETE FROM match WHERE id = ?", (id,))])

    def getDetails(self, match):
        return self.command('query', "SELECT * FROM detail WHERE match = ? ORDER BY datetime(time, '%Y-%m-%d %H:%M')", (match,))

    def delDetails(self, match):
        return self.command('update', "DELETE FROM detail WHERE match = ?", (match,))

    def insertDetail(self, match, id, code, time, team, player):
        return self.command('update', 'INSERT INTO detail VALUES (?, ?, ?, ?, ?, ?)', (match, id, time, code, team, player))

    def editDetail(self, id, code, time, team, player):
        return self.command('update', "UPDATE detail SET time = ?, type = ?, team = ?, player = ? WHERE id = ?", (time, code, team, player, id))

    def delDetail(self, id):
        return self.command('update', "DELETE FROM detail WHERE id = ?", (id,))

    def getHT(self, match):
        return self.command('query', "SELECT time, team FROM detail WHERE match = ?", (match,))

    def run(self):
        while True:
            id, req, cmd, val = self.request.get()
            res = True
            try:
                if req == 'query':
                    res = self.query(cmd, val)
                elif req == 'update':
                    self.update(cmd, val)
                elif req == 'updates':
                    self.updates(cmd)
                elif req == 'exit':
                    break
            except:
                res = False
            finally:
                self.result[id] = res

    def command(self, req, cmd, val = ()):
        id = uuid.uuid4().hex
        self.request.put((id, req, cmd, val))

        if cmd != 'exit':
            while True:
                if id in self.result:
                    res = self.result[id]
                    self.result.pop(id)
                    return res

    def start(self):
        if self.db_thread is None:
            self.db_thread = threading.Thread(target = self.run)
            self.db_thread.start()

    def stop(self):
        if self.db_thread is not None:
            self.command('exit', '')
            self.db_thread.join()
            self.db_thread = None

        self.con.close()
