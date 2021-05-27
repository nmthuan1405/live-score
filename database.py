import sqlite3
import os

class Database:
    def __init__(self, dbName = 'database.db'):
        isExists = os.path.isfile(dbName)

        self.con = sqlite3.connect(dbName, check_same_thread=False)
        self.cur = self.con.cursor()

        if not isExists:
            self.createTable()

    def __del__(self):
        self.con.close()
    
    def execute(self, cmd, val = ()):
        self.cur.execute(cmd, val)

    def query(self, cmd, val = ()):
        self.execute(cmd, val)
        return self.cur.fetchall()

    def insert(self, cmd, val = ()):
        self.execute(cmd, val)
        self.con.commit()

    def createTable(self):
        self.execute("CREATE TABLE auth(user text, pass text, isAdmin int, PRIMARY KEY (user))")
        self.execute("CREATE TABLE match(id text, team1 text, team2 text, score1 int, score2 int, time text, PRIMARY KEY (id))")
        self.execute("CREATE TABLE detail(id text, time int, type int, team int, player text, FOREIGN KEY (id) REFERENCES match(id))")

        self.insertAccount('admin', 'admin', True)

    def insertAccount(self, User, Pass, isAdmin = False):
        try:
            self.insert("INSERT INTO auth VALUES (?, ?, ?)", (User, Pass, int(isAdmin)))
            return True
        except sqlite3.IntegrityError:
            return False

    def checkAccount(self, User, Pass):
        data = self.query("SELECT * FROM auth WHERE user = ? AND pass = ?", (User, Pass))

        if (len(data) != 0):
            return bool(data[0][2])
        return None

    def insertMatch(self, id, team1Name, team2Name, time):
        try:
            self.insert("INSERT INTO match VALUES (?, ?, ?, 0, 0, ?)", (id, team1Name, team2Name, time))
            return True
        except sqlite3.IntegrityError:
            return False
