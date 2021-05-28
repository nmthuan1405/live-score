from doctest import master
from time import time
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.font import BOLD
from tkinter.messagebox import showerror, showinfo, askokcancel, showwarning
from tkinter import scrolledtext
from functools import partial
from tkcalendar import Calendar, DateEntry
import client
import queue
import uuid
import threading
from datetime import datetime

windowsGlo = list()

def center(toplevel):
    toplevel.update_idletasks()


    screen_width = toplevel.winfo_screenwidth()
    screen_height = toplevel.winfo_screenheight()

    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = screen_width/2 - size[0]/2
    y = screen_height/2 - size[1]/2

    toplevel.geometry("+%d+%d" % (x, y))

class ClientGUI:
    def __init__(self, master):
        #master.report_callback_exception = self.report_callback_exception
        self.services = None
        self.master = master
        self.master.title("Client")
        self.master.resizable(0, 0)
        self.master['padx'] = 20
        self.master['pady'] = 20

        self.master.columnconfigure(0, weight=2)
        self.master.columnconfigure(1, weight=2)
        self.master.columnconfigure(2, weight=1)

        self.master.bind('<Return>', self.handleReturn)
        self.master.bind('<Tab>', self.handleTab)
        self.master.bind('<Escape>', self.handleEsc)

        self.lbl_Title = Label(self.master, text = "LIVE SCORE", font=("Helvetica", 20))
        self.lbl_Title.grid(column = 0, row = 0, columnspan = 3, sticky = tk.N, padx = 0, pady = 0)

        self.lbl_IPInput = Label(self.master, text = "Server IP")
        self.lbl_IPInput.grid(column = 0, row = 1, sticky = tk.W, padx = 0, pady = 0)

        self.txt_IP_input = Entry(self.master)
        self.txt_IP_input.insert(-1, 'localhost')
        self.txt_IP_input.focus()
        self.txt_IP_input.grid(column = 0, row = 2, columnspan = 2, sticky = EW, padx = 0)

        self.btn_connect = Button(self.master, text="Connect", width = 10, command = self.connect)
        self.btn_connect.grid(column=2, row=2, sticky = tk.E, padx = 0, pady = 0)

        self.lbl_User = Label(self.master, text = "Username")
        self.lbl_User.grid(column = 0, row = 4, sticky = tk.W, padx = 0, pady = 0)

        self.txt_User = Entry(self.master)
        self.txt_User.grid(column = 0, row = 5, columnspan = 3, sticky = EW)
        self.txt_User.config(state = 'disabled')

        self.lbl_Password = Label(self.master, text = "Password")
        self.lbl_Password.grid(column = 0, row = 6, sticky = tk.W, padx = 0, pady = 0)

        self.txt_Password = Entry(self.master, show = "*")
        self.txt_Password.grid(column = 0, row = 7, columnspan = 3, sticky = EW)
        self.txt_Password.config(state = 'disabled')

        self.btn_SignUp = Button(self.master, text="Sign Up", command = self.signUp)
        self.btn_SignUp.grid(column=0, row=9, rowspan = 2, sticky = tk.SW, padx = 0, pady = 0, ipadx = 10)
        self.btn_SignUp.config(state = 'disabled')

        self.btn_SignIn = Button(self.master, text="Sign In", command = self.signIn)
        self.btn_SignIn.grid(column=1, row=9, rowspan = 2, sticky = tk.SW, padx = 0, pady = 0, ipadx = 10)
        self.btn_SignIn.config(state = 'disabled')

        self.btn_Exit = Button(self.master, text="Exit", command = self.exit)
        self.btn_Exit.grid(column=2, row=9, rowspan = 2, sticky = tk.SE, padx = 0, pady = 0, ipadx = 10)

        col_count, row_count = self.master.grid_size()

        for col in range(col_count):
            self.master.grid_columnconfigure(col, minsize = 90)
        
        for row in range(row_count):
            self.master.grid_rowconfigure(row, minsize = 15)

        self.master.protocol("WM_DELETE_WINDOW", self.exit)
    
    def report_callback_exception(self, *args):
        self.services = None
        # for windows in windowsGlo:
        #     windows.destroy()

        self.txt_IP_input.config(state = 'normal')
        self.btn_connect.config(text = 'Connect')
        # showerror(title = 'Error', message = 'Lost connection')

    def connect(self):
        if self.services == None:
            try:
                self.services = client.Client(self.txt_IP_input.get())
                self.services.connect()
            except:
                showerror(title = 'Error', message = 'Cannot connect to server.', parent = self.master)
                self.services = None
            else:
                self.txt_IP_input.config(state = 'disabled')
                self.btn_connect.config(text = 'Disconnect')
                showinfo("Sucess", "Connect to server sucessfully", parent = self.master)

                self.txt_User.config(state = 'normal')
                self.txt_Password.config(state = 'normal')
                self.btn_SignUp.config(state = 'normal')
                self.btn_SignIn.config(state = 'normal')
                self.txt_User.focus()

                self.txt_User.insert(-1, 'admin')
                self.txt_Password.insert(-1, 'admin')
        
        else:
            self.services.s_close()
            self.services = None

            self.txt_IP_input.config(state = 'normal')
            self.btn_connect.config(text = 'Connect')

            self.txt_User.config(state = 'disabled')
            self.txt_Password.config(state = 'disabled')
            self.btn_SignUp.config(state = 'disabled')
            self.btn_SignIn.config(state = 'disabled')
            self.txt_IP_input.focus()

    def handleReturn(self, event):
        if self.master.focus_get() == self.txt_IP_input or self.master.focus_get() == self.btn_connect:
            self.connect()
        elif self.master.focus_get() == self.txt_User or self.master.focus_get() == self.txt_Password or self.master.focus_get() == self.btn_SignIn:
            self.signIn()
        elif self.master.focus_get() == self.btn_SignUp:
            self.signUp()
        elif self.master.focus_get() == self.btn_Exit:
            self.exit()

    def handleTab(self, event):
        pass    # khong can code gi het

    def handleEsc(self, event):
        self.exit()

    def signUp(self):
        check = self.services.s_auth(self.txt_User.get(), self.txt_Password.get(), 'signUp')
        if check:
            showinfo('Sucess', 'Sign up sucessfully', parent = self.master)
        else:
            showerror('Error', 'Unable create account', parent = self.master)

    def signIn(self):
        self.services.isAdmin = self.services.s_auth(self.txt_User.get(), self.txt_Password.get(), 'signIn')
        if self.services.isAdmin is None:
            showerror(title = 'Error', message = 'Invalid username or password', parent = self.master)
            return

        window_user = Toplevel(self.master)
        userGUI(window_user, self.master, self.services)
        center(window_user)
        window_user.mainloop()

    def exit(self):
        if self.services != None:
            if not askokcancel("Exit", "Client is connecting.\nDo you want to disconnect?"):
                return
            
            self.services.s_close()
            
        self.master.destroy()

class userGUI:
    def __init__(self, master, parent, services):
        windowsGlo.append(master)

        self.master = master
        self.parent = parent
        self.services = services

        self.detailWindows = []
        self.request = queue.Queue()
        self.client_thread = None
        self.result = {}

        self.parent.withdraw()

        if self.services.isAdmin:
            self.master.title("Administrator")
        else:
            self.master.title("User")
        # self.master.resizable(0, 0)

        self.master.focus()
        self.master.grab_set()
        self.master['padx'] = 10
        self.master['pady'] = 10

        self.lbl_date = Label(self.master, text='Choose date:')
        self.lbl_date.place(x = 0, y = 0)

        self.txt_date = DateEntry(self.master, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.txt_date.place(x = 80, y = 0)

        self.isCheck = tk.IntVar()
        self.allDate = tk.Checkbutton(self.master, text = 'All Date', variable = self.isCheck, onvalue = 1, offvalue = 0, command = self.checker)
        self.allDate.place(x = 180, y = 0)

        if self.services.isAdmin:
            self.btn_edit = Button(self.master, text = "Edit match", width = 12, height = 1, command = self.edit)
            self.btn_edit.grid(column = 1, row = 1, sticky = tk.W, padx = 0, pady = 0, ipady = 0)

            self.btn_add = Button(self.master, text = "Add match", width = 12, height = 1, command = self.addMatch)
            self.btn_add.grid(column = 2, row = 1, sticky = tk.W, padx = 0, pady = 0, ipady = 0)

            self.btn_delete = Button(self.master, text = "Delete match", width = 12, height = 1, command = self.delete)
            self.btn_delete.grid(column = 3, row = 1, sticky = tk.W, padx = 0, pady = 0, ipady = 0)

            self.btn_editAccount = Button(self.master, text = "Edit account", width = 12, height = 1, command = partial(self.editAccount, self.master))
            self.btn_editAccount.grid(column = 5, row = 1, sticky = tk.E, padx = 0, pady = 0, ipady = 0)

        self.btn_detail = Button(self.master, text = "Match detail", width = 12, height = 1, command = partial(self.detail, self.master))
        self.btn_detail.grid(column = 0, row = 1, sticky = tk.W, padx = 0, pady = 0, ipady = 0)

        self.btn_signOut = Button(self.master, text = "Sign out", width = 12, height = 1, command = self.signOut)
        self.btn_signOut.grid(column = 6, row = 1, sticky = tk.E, padx = 0, pady = 0, ipady = 0)

        # columns
        columns = ('#1', '#2', '#3', '#4', '#5')
        self.tree = ttk.Treeview(self.master, columns = columns, show = 'headings', height = 20)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 12, BOLD))
        style.configure("Treeview", font=(None, 12))

        #config column width
        self.tree.column("#1", anchor = 'center', minwidth = 0, width = 0)
        self.tree.column("#2", anchor = 'center', minwidth = 50, width = 80)
        self.tree.column("#3", anchor = 'center', minwidth = 50, width = 220)
        self.tree.column("#4", anchor = 'center', minwidth = 50, width = 100)
        self.tree.column("#5", anchor = 'center', minwidth = 50, width = 220)

        # define headings
        self.tree.heading('#1', text='ID')
        self.tree.heading('#2', text='Time')
        self.tree.heading('#3', text='Team 1')
        self.tree.heading('#4', text='Score')
        self.tree.heading('#5', text='Team 2')

        self.tree.grid(row = 2, column = 0, padx = 0, pady = 5, columnspan = 7, sticky='nsew')

        # add a scrollbar
        self.scrollbar = ttk.Scrollbar(self.master, orient = tk.VERTICAL, command = self.tree.yview)
        self.tree.configure(yscroll = self.scrollbar.set)
        self.scrollbar.grid(row = 2, column = 7, padx = 0, pady = 5, sticky = 'ns')
        
        col_count, row_count = self.master.grid_size()
        for col in range(col_count):
            self.master.grid_columnconfigure(col, minsize = 0)
        for row in range(row_count):
            self.master.grid_rowconfigure(row, minsize = 30)

        self.master.protocol("WM_DELETE_WINDOW", self.signOut)

        self.start()
        self.updateMatch()

        def dateChanged(event):
            selectedDate = self.txt_date.get_date()
            self.allDate.deselect()
        self.txt_date.bind('<<DateEntrySelected>>', dateChanged)



    def checker(self):
        if self.isCheck.get() == 0:
            self.txt_date.config(state = 'normal')
            # khi bo chon all date thi hien thi lai ds tran dau cua ngay trong txt_date
        if self.isCheck.get() == 1:
            self.txt_date.config(state = 'disabled')

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
            if cmd == 'exit':
                break

            self.result[id] = res

    def start(self):
        if self.client_thread is None:
            self.client_thread = threading.Thread(target = self.run)
            self.client_thread.start()

    def stop(self):
        if self.client_thread is not None:
            self.command('exit', '')
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


    def updateMatch(self):
        matches_tuple = self.command('listAll')
        matches = [list(ele) for ele in matches_tuple]

        choosen = self.tree.item(self.tree.focus())['values']
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        for match in matches:
            self.tree.insert('', tk.END, values = match[:-1])
        
        if choosen != '':
            id = None
            for row in self.tree.get_children():
                if self.tree.item(row)['values'][0] == choosen[0]:
                    id = row
                    break

            if id is not None: 
                self.tree.selection_set(id)   
                self.tree.focus(id)

        self.master.after(1000, self.updateMatch)

    def detail(self, parent):
        match = self.tree.item(self.tree.focus())['values']
        if match == '':
            showwarning("Warning", "Choose a match to see detail")
            return

        window_detail = Toplevel(self.master)
        self.detailWindows.append(detailGUI(window_detail, self, self.services, match))
        center(window_detail)
        window_detail.mainloop()


    def edit(self):
        match = self.tree.item(self.tree.focus())['values']
        if match == '':
            return

        window_edit = Toplevel(self.master)
        addMatchGUI(window_edit, self, self.services, match[0])
        center(window_edit)
        window_edit.mainloop()

    def addMatch(self):
        window_addMatch = Toplevel(self.master)
        addMatchGUI(window_addMatch, self, self.services)
        center(window_addMatch)
        window_addMatch.mainloop()

    def delete(self):
        match = self.tree.item(self.tree.focus())['values']
        if match == '':
            return

        if not self.command('delMatch', match[0]):
            showerror('Error', 'Unable to delete match')        

    def editAccount(self, parent):
        window_editAccount = Toplevel(self.master)
        editAccountGUI(window_editAccount, parent, self.services)
        center(window_editAccount)
        window_editAccount.mainloop()

    def signOut(self):
        self.services.s_signOut()
        self.stop()

        self.master.destroy()
        windowsGlo.remove(self.master)

        self.parent.deiconify()

class addMatchGUI:
    def __init__(self, master, parent, services, match = None):
        windowsGlo.append(master)
        self.services = services
        self.master = master
        if match is None:
            self.master.title("Add match")
        else:
            self.master.title("Edit match")
        # self.master.resizable(0, 0)
        self.master.focus()
        self.master.grab_set()
        self.master['padx'] = 10
        self.master['pady'] = 10

        self.parent = parent

        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)
        self.master.columnconfigure(2, weight=1)

        self.lbl_ID = Label(self.master, text = 'ID')
        self.lbl_ID.grid(row = 0, column = 0, sticky = W)

        self.txt_ID = Entry(self.master)
        self.txt_ID.focus()
        self.txt_ID.grid(row = 1, column = 0, columnspan = 3, sticky = EW, padx = 0)
        
        if (match is not None):
            self.txt_ID.insert(-1, match)
            self.txt_ID.config(state = 'disabled')
        else:
            self.txt_ID.grid(row = 1, column = 0, columnspan = 2, sticky = EW, padx = 0)
            self.isCheck = tk.IntVar()
            self.isDefault = tk.Checkbutton(self.master, text = 'Default', variable = self.isCheck, onvalue = 1, offvalue = 0, command = self.checker)
            self.isDefault.grid(row = 1, column = 2, sticky = E)

        self.lbl_team1 = Label(self.master, text = '1st Team')
        self.lbl_team1.grid(row = 2, column = 0, sticky = W)

        self.txt_team1 = Entry(self.master)
        self.txt_team1.grid(row = 3, column = 0, columnspan = 3, sticky = EW, padx = 0)

        self.lbl_team2 = Label(self.master, text = '2nd Team')
        self.lbl_team2.grid(row = 4, column = 0, sticky = W)

        self.txt_team2 = Entry(self.master)
        self.txt_team2.grid(row = 5, column = 0, columnspan = 3, sticky = EW, padx = 0)

        self.lbl_time = Label(self.master, text = 'Time')
        self.lbl_time.grid(row = 6, column = 0, sticky = W)

        self.txt_date = DateEntry(self.master, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.txt_date.grid(row = 7, column = 0)

        self.currHour = tk.IntVar(value = 0)
        self.spinHour = ttk.Spinbox(self.master, from_=0, to=23, width = 5, textvariable=self.currHour, wrap=True)
        self.spinHour.grid(row = 7, column = 1, sticky = E)

        self.lbl_seperator = Label(self.master, text = ':', font=(None, 12, BOLD))
        self.lbl_seperator.grid(row = 7, column = 2, sticky = W, padx = 4)

        self.currMin = tk.IntVar(value = 0)
        self.spinMin = ttk.Spinbox(self.master, from_=0, to=59, width = 5, textvariable=self.currMin, wrap=True)
        self.spinMin.grid(row = 7, column = 2, sticky = E)

        if match is not None:
            self.btn_change = Button(self.master, text="Change", command = self.change, width = 8)
            self.btn_change.grid(row = 9, column = 1, sticky = tk.W, padx = 0, pady = 0, ipadx = 0)
        else:
            self.btn_add = Button(self.master, text="Add", command = self.add, width = 8)
            self.btn_add.grid(row = 9, column = 1, sticky = tk.W, padx = 0, pady = 0, ipadx = 0)

        self.btn_cancel = Button(self.master, text="Cancel", command = self.on_closing, width = 8)
        self.btn_cancel.grid(row = 9, column = 2, sticky = tk.S, padx = 0, pady = 0, ipadx = 0)

        col_count, row_count = self.master.grid_size()
        for col in range(col_count):
            self.master.grid_columnconfigure(col, minsize = 70)
        for row in range(row_count):
            self.master.grid_rowconfigure(row, minsize = 15)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        if match is not None:
            data = self.parent.command('getMatch', match)
            if data and len(data) == 1:
                data = data[0]

                self.txt_team1.insert(-1, data[2])
                self.txt_team2.insert(-1, data[3])

                date = datetime.strptime(data[1], '%Y-%m-%d %H:%M')
                self.txt_date.set_date(date)
                self.spinHour.delete(0, END)
                self.spinHour.insert(-1, date.hour)
                self.spinMin.delete(0, END)
                self.spinMin.insert(-1, date.minute)

    def on_closing(self):
        self.master.destroy()
        self.parent.master.focus()
        self.parent.master.grab_set()

        windowsGlo.remove(self.master)

    def checker(self):
        if self.isCheck.get() == 0:
            self.txt_ID.config(state = 'normal')
            self.txt_ID.delete(0, END)
        if self.isCheck.get() == 1:
            self.txt_ID.delete(0, END)
            self.txt_ID.insert(-1, uuid.uuid4().hex)
            self.txt_ID.config(state = 'readonly')

    def change(self):
        id = self.txt_ID.get()
        team1 = self.txt_team1.get()
        team2 = self.txt_team2.get()
        hour = self.spinHour.get()
        min = self.spinMin.get()

        if team1 == '' or team2 == '':
            showerror('Erorr', 'Invalid input')
            return

        time = str(self.txt_date.get_date()) + ' ' + hour + ':' + min
        if not self.parent.command('editMatch', (id, team1, team2, time)):
            showerror('Error', 'Unable to create new match')

    def add(self):

        id = self.txt_ID.get()
        team1 = self.txt_team1.get()
        team2 = self.txt_team2.get()
        hour = self.spinHour.get()
        min = self.spinMin.get()

        if id == '' or team1 == '' or team2 == '':
            showerror('Erorr', 'Invalid input')
            return

        time = str(self.txt_date.get_date()) + ' ' + hour + ':' + min
        if not self.parent.command('addMatch', (id, team1, team2, time)):
            showerror('Error', 'Unable to create new match')

        self.txt_ID.config(state = 'normal')
        self.txt_ID.delete(0, END)
        self.txt_ID.insert(-1, uuid.uuid4().hex)
        self.txt_ID.config(state = 'readonly')



class editAccountGUI:
    def __init__(self, master, parent, services):
        windowsGlo.append(master)
        self.services = services
        self.master = master
        self.master.title("Edit account")
        # self.master.resizable(0, 0)
        self.master.focus()
        self.master.grab_set()
        self.master['padx'] = 10
        self.master['pady'] = 10

        self.parent = parent

        self.btn_edit = Button(self.master, text="Edit", command = partial(self.edit, self.master), width = 8)
        self.btn_edit.grid(row = 0, column = 0, sticky = tk.W, padx = 0, pady = 0, ipadx = 0)

        self.btn_add = Button(self.master, text="Add", command = partial(self.add, self.master), width = 8)
        self.btn_add.grid(row = 0, column = 1, padx = 0, pady = 0, ipadx = 0)

        self.btn_delete = Button(self.master, text="Delete", command = self.delete, width = 8)
        self.btn_delete.grid(row = 0, column = 2, sticky = tk.E, padx = 0, pady = 0, ipadx = 0)

        # columns
        columns = ('#1', '#2', '#3')
        self.tree = ttk.Treeview(self.master, columns = columns, show = 'headings', height = 20)

        # style = ttk.Style()
        # style.configure("Treeview.Heading", font=(None, 12, BOLD))
        # style.configure("Treeview", font=(None, 12))

        #config column width
        self.tree.column("#1", anchor = 'center', minwidth = 50, width = 150)
        self.tree.column("#2", anchor = 'center', minwidth = 50, width = 150)
        self.tree.column("#3", anchor = 'center', minwidth = 50, width = 100)

        # define headings
        self.tree.heading('#1', text='Username')
        self.tree.heading('#2', text='Password')
        self.tree.heading('#3', text='Is admin')

        self.tree.grid(row = 1, column = 0, padx = 0, pady = 5, columnspan = 3, sticky='nsew')

        # add a scrollbar
        self.scrollbar = ttk.Scrollbar(self.master, orient = tk.VERTICAL, command = self.tree.yview)
        self.tree.configure(yscroll = self.scrollbar.set)
        self.scrollbar.grid(row = 1, column = 3, padx = 0, pady = 5, sticky = 'ns')

        # add data
        contacts = []
        contacts.append(('admin', 'admin', 'Yes'))
        contacts.append(('user', 'user', 'No', '2 - 1'))
        for contact in contacts:
            self.tree.insert('', tk.END, values=contact)
        
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def edit(self, parent):
        account = self.tree.item(self.tree.focus())['values']
        if account == '':
            return

        window_edit = Toplevel(self.master)
        editGUI(window_edit, parent, self.services, account)
        center(window_edit)
        window_edit.mainloop()

    def add(self, parent):
        window_add = Toplevel(self.master)
        editGUI(window_add, parent, self.services, None)
        center(window_add)
        window_add.mainloop()

    def delete(self):
        pass

    def on_closing(self):
        self.master.destroy()
        self.parent.focus()
        self.parent.grab_set()
        windowsGlo.remove(self.master)

class editGUI:
    def __init__(self, master, parent, services, account):
        windowsGlo.append(master)
        self.services = services
        self.master = master
        if account is not None:
            self.master.title("Edit Account")
        else:
            self.master.title("Add Account")
        # self.master.resizable(0, 0)
        self.master.focus()
        self.master.grab_set()
        self.master['padx'] = 10
        self.master['pady'] = 10

        self.parent = parent

        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)
        self.master.columnconfigure(2, weight=1)

        self.lbl_user = Label(self.master, text = 'Username')
        self.lbl_user.grid(row = 0, column = 0, sticky = W)

        self.txt_user = Entry(self.master)
        self.txt_user.focus()
        self.txt_user.grid(row = 1, column = 0, columnspan = 3, sticky = EW, padx = 0)

        self.lbl_pass = Label(self.master, text = 'Password')
        self.lbl_pass.grid(row = 2, column = 0, sticky = W)

        self.txt_pass = Entry(self.master)
        self.txt_pass.grid(row = 3, column = 0, columnspan = 3, sticky = EW, padx = 0)

        self.isCheck = tk.IntVar()
        self.isAdmin = tk.Checkbutton(self.master, text = 'Is admin', variable = self.isCheck, onvalue = 1, offvalue = 0)
        self.isAdmin.grid(row = 4, column = 0, sticky = W)
        # De lay gia tri checkbox:
        # self.isCheck.get() == 1   #1: la admin

        self.btn_cancel = Button(self.master, text="Cancel", command = self.cancel, width = 8)
        self.btn_cancel.grid(row = 6, column = 2, sticky = tk.S, padx = 0, pady = 0, ipadx = 0)

        if account is not None:
            self.txt_user.insert(-1, account[0])
            self.txt_pass.insert(-1, account[1])
            if account[2] == 'Yes':
                self.isAdmin.select()

            self.btn_change = Button(self.master, text="Change", command = self.change, width = 8)
            self.btn_change.grid(row = 6, column = 1, sticky = tk.W, padx = 0, pady = 0, ipadx = 0)
        else:
            self.btn_add = Button(self.master, text="Add", command = self.add, width = 8)
            self.btn_add.grid(row = 6, column = 1, sticky = tk.W, padx = 0, pady = 0, ipadx = 0)

        col_count, row_count = self.master.grid_size()
        for col in range(col_count):
            self.master.grid_columnconfigure(col, minsize = 73)
        for row in range(row_count):
            self.master.grid_rowconfigure(row, minsize = 15)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.master.destroy()
        self.parent.focus()
        self.parent.grab_set()
        windowsGlo.remove(self.master)

    def change(self):
        pass

    def add(self):
        pass

    def cancel(self):
        self.on_closing()


class detailGUI:
    def __init__(self, master, parent, services, match):
        windowsGlo.append(master)
        self.services = services
        self.master = master
        if self.services.isAdmin:
            self.master.title("Match details")
        else:
            self.master.title("Edit match")
        # self.master.resizable(0, 0)
        self.master.focus()
        # self.master.grab_set()    # Bo lock parent GUI
        self.master['padx'] = 10
        self.master['pady'] = 10

        self.parent = parent

        self.lbl_ID = Label(self.master, text = match[0], font=(None, 12))

        self.lbl_time = Label(self.master, text = match[1], font=(None, 12))

        self.lbl_team1 = Label(self.master, text = match[2], font=(None, 14))

        self.lbl_score = Label(self.master, text = match[3], font=(None, 14))

        self.lbl_team2 = Label(self.master, text = match[4], font=(None, 14))

        if self.services.isAdmin:
            self.btn_addGoal = Button(self.master, text = "Add goal", width = 10, height = 1, command = partial(self.addEvent, match, 0, self.master))
            self.btn_addGoal.place(x = 10, y = 0)

            self.btn_addTag = Button(self.master, text = "Add tag", width = 10, height = 1, command = partial(self.addEvent, match, 1, self.master))
            self.btn_addTag.place(x = 100, y = 0)

            self.btn_addOthers = Button(self.master, text = "Add others", width = 10, height = 1, command = partial(self.addOthers, match, self.master))
            self.btn_addOthers.place(x = 190, y = 0)

            self.lbl_ID.place(x = 10, y = 30)
            self.lbl_time.place( x = 50, y = 30)
            self.master.update()
            self.lbl_team1.place(x = (60+(180+120)/2-self.lbl_team1.winfo_reqwidth()/2), y = 30)
            self.lbl_score.place(x = (60+180+120+(70)/2-self.lbl_score.winfo_reqwidth()/2), y = 30)
            self.lbl_team2.place(x = (60+180+120+70+(120+180)/2-self.lbl_team2.winfo_reqwidth()/2), y = 30)
        else:
            self.lbl_ID.place(x = 10, y = 0)
            self.lbl_time.place( x = 50, y = 0)
            self.master.update()
            self.lbl_team1.place(x = (60+(180+120)/2-self.lbl_team1.winfo_reqwidth()/2), y = 0)
            self.lbl_score.place(x = (60+180+120+(70)/2-self.lbl_score.winfo_reqwidth()/2), y = 0)
            self.lbl_team2.place(x = (60+180+120+70+(120+180)/2-self.lbl_team2.winfo_reqwidth()/2), y = 0)

        # columns
        columns = ('#1', '#2', '#3', '#4', '#5', '#6')
        self.tree = ttk.Treeview(self.master, columns = columns, show = 'headings', height = 20)

        #config column width
        self.tree.column("#1", anchor = 'center', minwidth = 50, width = 60)
        self.tree.column("#2", anchor = 'center', minwidth = 50, width = 180)
        self.tree.column("#3", anchor = 'center', minwidth = 50, width = 120)
        self.tree.column("#4", anchor = 'center', minwidth = 50, width = 70)
        self.tree.column("#5", anchor = 'center', minwidth = 50, width = 120)
        self.tree.column("#6", anchor = 'center', minwidth = 50, width = 180)

        # define headings
        self.tree.heading('#1', text='Time')
        self.tree.heading('#2', text='Team 1 player')
        self.tree.heading('#3', text='Event')
        self.tree.heading('#4', text='Score')
        self.tree.heading('#5', text='Event')
        self.tree.heading('#6', text='Team 2 player')

        if type == 0:
            self.tree.grid(row = 1, column = 0, padx = 0, pady = 5, columnspan = 5, sticky='nsew')
        else:
            self.tree.grid(row = 2, column = 0, padx = 0, pady = 5, columnspan = 5, sticky='nsew')

        # add a scrollbar
        self.scrollbar = ttk.Scrollbar(self.master, orient = tk.VERTICAL, command = self.tree.yview)
        self.tree.configure(yscroll = self.scrollbar.set)
        if type == 0:
            self.scrollbar.grid(row = 1, column = 5, padx = 0, pady = 5, sticky = 'ns')
        else:
            self.scrollbar.grid(row = 2, column = 5, padx = 0, pady = 5, sticky = 'ns')

        # add data
        contacts = []
        contacts.append(("10'", 'A', 'Score', '1 - 0', '', ''))
        contacts.append(("20'", '', '', '1 - 1', 'Score', 'B'))

        for contact in contacts:
            self.tree.insert('', tk.END, values=contact)

        col_count, row_count = self.master.grid_size()
        for col in range(col_count):
            self.master.grid_columnconfigure(col, minsize = 0)
        
        for row in range(row_count):
            self.master.grid_rowconfigure(row, minsize = 30)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.master.destroy()
        self.parent.focus()
        self.parent.grab_set()
        windowsGlo.remove(self.master)

    def addEvent(self, match, type, parent):
        window_addEvent = Toplevel(self.master)
        addEventGUI(window_addEvent, type, parent, self.services, match)
        center(window_addEvent)
        window_addEvent.mainloop()

    def addOthers(self, match, parent):
        window_addOthers = Toplevel(self.master)
        addOthersGUI(window_addOthers, parent, self.services, match)
        center(window_addOthers)
        window_addOthers.mainloop()

class addEventGUI:
    def __init__(self, master, type, parent, services, match):
        windowsGlo.append(master)
        self.services = services
        self.master = master
        if type == 0:
            self.master.title("Add goal")
        else:
            self.master.title("Add tag")
        # self.master.resizable(0, 0)
        self.master.focus()
        self.master.grab_set()
        self.master['padx'] = 10
        self.master['pady'] = 10
        self.parent = parent

        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)
        self.master.columnconfigure(2, weight=1)

        self.lbl_team = Label(self.master, text = 'Team')
        self.lbl_team.grid(column = 0, row = 0, sticky = W)

        self.teams = (match[2], match[4])
        self.selected_team = tk.StringVar()
        self.cbb_team = ttk.Combobox(self.master, textvariable = self.selected_team)
        self.cbb_team['values'] = self.teams
        self.cbb_team.current(0)
        self.cbb_team['state'] = 'readonly'  # normal
        self.cbb_team.grid(column = 0, row = 1, columnspan = 3, sticky = EW, padx = 0, pady = 0)

        self.lbl_player = Label(self.master, text = 'Player')
        self.lbl_player.grid(column = 0, row = 2, sticky = W)

        self.txt_player = Entry(self.master)
        self.txt_player.grid(column = 0, row = 3, columnspan = 3, sticky = EW, padx = 0, pady = 0)

        self.lbl_time = Label(self.master, text = 'Time')
        self.lbl_time.grid(column = 0, row = 7, sticky = W)

        self.isCheck = tk.IntVar()
        self.checkbox = tk.Checkbutton(self.master, text = 'default', variable = self.isCheck, onvalue = 1, offvalue = 0, command = self.checker)
        self.checkbox.select()
        self.checkbox.place( x = 35, y = 143)

        self.txt_time = Entry(self.master)
        self.txt_time.insert(-1, 'now')
        self.txt_time.config(state = 'disabled')
        self.txt_time.config(state = 'readonly')
        self.txt_time.grid(column = 0, row = 8, columnspan = 3, sticky = EW, padx = 0, pady = 0)

        if type == 1:
            self.lbl_tag = Label(self.master, text = 'Tag')
            self.lbl_tag.grid(column = 0, row = 4, sticky = W)

            self.tags = ('Yellow card', 'Red card')
            self.selected_tag = tk.StringVar()
            self.cbb_tag = ttk.Combobox(self.master, textvariable = self.selected_tag)
            self.cbb_tag['values'] = self.tags
            self.cbb_tag.current(0)
            self.cbb_tag['state'] = 'readonly'  # normal
            self.cbb_tag.grid(column = 0, row = 5, columnspan = 3, sticky = EW, padx = 0, pady = 0)

        self.btn_add = Button(self.master, text="Add", command = self.add, width = 8)
        self.btn_add.grid(row = 10, column = 1, sticky = tk.W, padx = 0, pady = 0, ipadx = 0)

        self.btn_cancel = Button(self.master, text="Cancel", command = self.cancel, width = 8)
        self.btn_cancel.grid(row = 10, column = 2, sticky = tk.S, padx = 0, pady = 0, ipadx = 0)

        col_count, row_count = self.master.grid_size()
        for col in range(col_count):
            self.master.grid_columnconfigure(col, minsize = 70)
        for row in range(row_count):
            self.master.grid_rowconfigure(row, minsize = 20)

    def checker(self):
        if self.isCheck.get() == 0:
            self.txt_time.config(state = 'normal')
            self.txt_time.delete(0, END)
        if self.isCheck.get() == 1:
            self.txt_time.delete(0, END)
            self.txt_time.insert(-1, 'now')
            self.txt_time.config(state = 'readonly')

    def add(self):
        pass
    def cancel(self):
        self.master.destroy()
        windowsGlo.remove(self.master)

class addOthersGUI:
    def __init__(self, master, parent, services, match):
        windowsGlo.append(master)
        self.services = services
        self.master = master
        self.master.title("Add event")
        # self.master.resizable(0, 0)
        self.master.focus()
        self.master.grab_set()
        self.master['padx'] = 10
        self.master['pady'] = 10
        self.parent = parent

        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)
        self.master.columnconfigure(2, weight=1)

        self.lbl_event = Label(self.master, text = 'Event')
        self.lbl_event.grid(column = 0, row = 0, sticky = W)

        self.events = ('Half-time break ', 'Stoppage time')
        self.selected_event = tk.StringVar()
        self.cbb_event = ttk.Combobox(self.master, textvariable = self.selected_event)
        self.cbb_event['values'] = self.events
        self.cbb_event.current(0)
        self.cbb_event['state'] = 'readonly'  # normal
        self.cbb_event.grid(column = 0, row = 1, columnspan = 3, sticky = EW, padx = 0, pady = 0)

        self.lbl_time = Label(self.master, text = 'Time')
        self.lbl_time.grid(column = 0, row = 2, sticky = W)

        self.isCheck = tk.IntVar()
        self.checkbox = tk.Checkbutton(self.master, text = 'default', variable = self.isCheck, onvalue = 1, offvalue = 0, command = self.checker)
        self.checkbox.select()
        self.checkbox.place( x = 35, y = 42)

        self.txt_time = Entry(self.master)
        self.txt_time.insert(-1, 'now')
        self.txt_time.config(state = 'readonly')
        self.txt_time.grid(column = 0, row = 3, columnspan = 3, sticky = EW, padx = 0, pady = 0)

        self.lbl_duration = Label(self.master, text = 'Duration')
        self.lbl_duration.grid(column = 0, row = 4, sticky = W)

        self.currDur = tk.IntVar(value = 15)
        self.spinDur = ttk.Spinbox(self.master, width = 8, from_=0, to=30, textvariable=self.currDur, wrap=True)
        self.spinDur.grid(row = 5, column = 0, columnspan = 1, sticky = W)

        self.lbl_min = Label(self.master, text = 'minutes')
        self.lbl_min.grid(row = 5, column = 1, sticky = W)
        
        self.btn_add = Button(self.master, text="Add", command = self.add, width = 8)
        self.btn_add.grid(row = 7, column = 1, sticky = tk.W, padx = 0, pady = 0, ipadx = 0)

        self.btn_cancel = Button(self.master, text="Cancel", command = self.cancel, width = 8)
        self.btn_cancel.grid(row = 7, column = 2, sticky = tk.S, padx = 0, pady = 0, ipadx = 0)

        col_count, row_count = self.master.grid_size()
        for col in range(col_count):
            self.master.grid_columnconfigure(col, minsize = 70)
        for row in range(row_count):
            self.master.grid_rowconfigure(row, minsize = 20)
    
    def checker(self):
        if self.isCheck.get() == 0:
            self.txt_time.config(state = 'normal')
            self.txt_time.delete(0, END)
        if self.isCheck.get() == 1:
            self.txt_time.delete(0, END)
            self.txt_time.insert(-1, 'now')
            self.txt_time.config(state = 'readonly')

    def add(self):
        pass

    def cancel(self):
        self.master.destroy()
        windowsGlo.remove(self.master)


window_client = Tk()
ClientGUI(window_client)
center(window_client)
window_client.mainloop()