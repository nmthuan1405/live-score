from doctest import master
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.font import BOLD
from tkinter.messagebox import showerror, showinfo, askokcancel
from tkinter import scrolledtext
from functools import partial
import client

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

        self.parent.withdraw()

        if self.services.isAdmin:\
            self.master.title("Administrator")
        else:
            self.master.title("User")
        # self.master.resizable(0, 0)

        self.master.focus()
        self.master.grab_set()
        self.master['padx'] = 10
        self.master['pady'] = 10

        if self.services.isAdmin:
            self.btn_edit = Button(self.master, text = "Edit match", width = 12, height = 2, command = partial(self.edit, self.master))
            self.btn_edit.grid(column = 1, row = 0, sticky = tk.W, padx = 0, pady = 0, ipady = 0)

            self.btn_add = Button(self.master, text = "Add match", width = 12, height = 2, command = partial(self.addMatch, self.master))
            self.btn_add.grid(column = 2, row = 0, sticky = tk.W, padx = 0, pady = 0, ipady = 0)

            self.btn_delete = Button(self.master, text = "Delete match", width = 12, height = 2, command = self.delete)
            self.btn_delete.grid(column = 3, row = 0, sticky = tk.W, padx = 0, pady = 0, ipady = 0)

            self.btn_editAccount = Button(self.master, text = "Edit account", width = 12, height = 2, command = partial(self.editAccount, self.master))
            self.btn_editAccount.grid(column = 5, row = 0, sticky = tk.E, padx = 0, pady = 0, ipady = 0)

        self.btn_detail = Button(self.master, text = "Match detail", width = 12, height = 2, command = partial(self.detail, self.master))
        self.btn_detail.grid(column = 0, row = 0, sticky = tk.W, padx = 0, pady = 0, ipady = 0)

        self.btn_signOut = Button(self.master, text = "Sign out", width = 12, height = 2, command = self.signOut)
        self.btn_signOut.grid(column = 6, row = 0, sticky = tk.E, padx = 0, pady = 0, ipady = 0)

        # columns
        columns = ('#1', '#2', '#3', '#4', '#5')
        self.tree = ttk.Treeview(self.master, columns = columns, show = 'headings', height = 20)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 12, BOLD))
        style.configure("Treeview", font=(None, 12))

        #config column width
        self.tree.column("#1", anchor = 'center', minwidth = 50, width = 50)
        self.tree.column("#2", anchor = 'center', minwidth = 50, width = 80)
        self.tree.column("#3", anchor = 'center', minwidth = 50, width = 200)
        self.tree.column("#4", anchor = 'center', minwidth = 50, width = 80)
        self.tree.column("#5", anchor = 'center', minwidth = 50, width = 200)

        # define headings
        self.tree.heading('#1', text='ID')
        self.tree.heading('#2', text='Time')
        self.tree.heading('#3', text='Team 1')
        self.tree.heading('#4', text='Score')
        self.tree.heading('#5', text='Team 2')

        self.tree.grid(row = 1, column = 0, padx = 0, pady = 5, columnspan = 7, sticky='nsew')

        # add a scrollbar
        self.scrollbar = ttk.Scrollbar(self.master, orient = tk.VERTICAL, command = self.tree.yview)
        self.tree.configure(yscroll = self.scrollbar.set)
        self.scrollbar.grid(row = 1, column = 7, padx = 0, pady = 5, sticky = 'ns')

        # add data
        contacts = []
        contacts.append(('1', '22:10', 'Verona', '1 - 1', 'Bologna'))
        contacts.append(('2', '17:00', 'Campbelltown City', '2 - 1', 'North Eastern Metro Stars'))
        for contact in contacts:
            self.tree.insert('', tk.END, values=contact)
        
        self.master.protocol("WM_DELETE_WINDOW", self.signOut)

    def detail(self, parent):
        match = self.tree.item(self.tree.focus())['values']
        if match == '':
            return

        window_detail = Toplevel(self.master)
        if self.services.isAdmin:
            detailGUI(window_detail, 1, parent, self.services, match)
        else:
            detailGUI(window_detail, 0, parent, self.services, match)
        center(window_detail)
        window_detail.mainloop()

    def edit(self, parent):
        match = self.tree.item(self.tree.focus())['values']
        if match == '':
            return

        window_edit = Toplevel(self.master)
        addMatchGUI(window_edit, parent, self.services, match)
        center(window_edit)
        window_edit.mainloop()

    def addMatch(self, parent):
        window_addMatch = Toplevel(self.master)
        addMatchGUI(window_addMatch, parent, self.services, None)
        center(window_addMatch)
        window_addMatch.mainloop()

    def delete(self):
        pass

    def editAccount(self, parent):
        window_editAccount = Toplevel(self.master)
        editAccountGUI(window_editAccount, parent, self.services)
        center(window_editAccount)
        window_editAccount.mainloop()

    def signOut(self):
        self.services.s_signOut()

        self.master.destroy()
        windowsGlo.remove(self.master)

        self.parent.deiconify()

class addMatchGUI:
    def __init__(self, master, parent, services, match):
        windowsGlo.append(master)
        self.services = services
        self.master = master
        if match == None:
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
        if(match != None):
            self.txt_ID.insert(-1, match[0])

        self.lbl_team1 = Label(self.master, text = 'Team 1')
        self.lbl_team1.grid(row = 2, column = 0, sticky = W)

        self.txt_team1 = Entry(self.master)
        self.txt_team1.grid(row = 3, column = 0, columnspan = 3, sticky = EW, padx = 0)
        if(match != None):
            self.txt_team1.insert(-1, match[2])

        self.lbl_team2 = Label(self.master, text = 'Team 2')
        self.lbl_team2.grid(row = 4, column = 0, sticky = W)

        self.txt_team2 = Entry(self.master)
        self.txt_team2.grid(row = 5, column = 0, columnspan = 3, sticky = EW, padx = 0)
        if(match != None):
            self.txt_team2.insert(-1, match[4])

        self.lbl_time = Label(self.master, text = 'Time')
        self.lbl_time.grid(row = 6, column = 0, sticky = W)

        self.txt_time = Entry(self.master)
        self.txt_time.grid(row = 7, column = 0, columnspan = 3, sticky = EW, padx = 0)
        if(match != None):
            self.txt_time.insert(-1, match[1])

        if match !=None:
            self.btn_change = Button(self.master, text="Change", command = self.change, width = 8)
            self.btn_change.grid(row = 9, column = 1, sticky = tk.W, padx = 0, pady = 0, ipadx = 0)
        else:
            self.btn_add = Button(self.master, text="Add", command = self.add, width = 8)
            self.btn_add.grid(row = 9, column = 1, sticky = tk.W, padx = 0, pady = 0, ipadx = 0)

        self.btn_cancel = Button(self.master, text="Cancel", command = self.cancel, width = 8)
        self.btn_cancel.grid(row = 9, column = 2, sticky = tk.S, padx = 0, pady = 0, ipadx = 0)

        col_count, row_count = self.master.grid_size()
        for col in range(col_count):
            self.master.grid_columnconfigure(col, minsize = 70)
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
        self.master.destroy()
        windowsGlo.remove(self.master)

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

        self.tree.grid(row = 1, column = 0, padx = 0, pady = 5, columnspan = 1, sticky='nsew')

        # add a scrollbar
        self.scrollbar = ttk.Scrollbar(self.master, orient = tk.VERTICAL, command = self.tree.yview)
        self.tree.configure(yscroll = self.scrollbar.set)
        self.scrollbar.grid(row = 1, column = 1, padx = 0, pady = 5, sticky = 'ns')

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
        self.master.title("Edit Account")
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
        self.txt_user.insert(-1, account[0])

        self.lbl_pass = Label(self.master, text = 'Password')
        self.lbl_pass.grid(row = 2, column = 0, sticky = W)

        self.txt_pass = Entry(self.master)
        self.txt_pass.grid(row = 3, column = 0, columnspan = 3, sticky = EW, padx = 0)
        self.txt_pass.insert(-1, account[1])

        self.isCheck = tk.IntVar()
        self.isAdmin = tk.Checkbutton(self.master, text = 'Is admin', variable = self.isCheck, onvalue = 1, offvalue = 0)
        if account[2] == 'Yes':
            self.isAdmin.select()
        self.isAdmin.grid(row = 4, column = 0, sticky = W)
        # De lay gia tri checkbox:
        # self.isCheck.get() == 1   #1: la admin

        self.btn_change = Button(self.master, text="Change", command = self.change, width = 8)
        self.btn_change.grid(row = 6, column = 1, sticky = tk.W, padx = 0, pady = 0, ipadx = 0)

        self.btn_cancel = Button(self.master, text="Cancel", command = self.cancel, width = 8)
        self.btn_cancel.grid(row = 6, column = 2, sticky = tk.S, padx = 0, pady = 0, ipadx = 0)

        col_count, row_count = self.master.grid_size()
        for col in range(col_count):
            self.master.grid_columnconfigure(col, minsize = 72)
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

    def cancel(self):
        self.on_closing()


class detailGUI:
    def __init__(self, master, type, parent, services, match):
        windowsGlo.append(master)
        self.services = services
        self.master = master
        if type == 0:
            self.master.title("Match details")
        else:
            self.master.title("Edit match")
        # self.master.resizable(0, 0)
        self.master.focus()
        # self.master.grab_set()
        self.master['padx'] = 10
        self.master['pady'] = 10

        self.parent = parent

        self.lbl_ID = Label(self.master, text = match[0], font=(None, 12))
        self.lbl_ID.place(x = 10, y = 0)

        self.lbl_time = Label(self.master, text = match[1], font=(None, 12))
        self.lbl_time.place( x = 50, y = 0)

        self.lbl_team1 = Label(self.master, text = match[2], font=(None, 14))
        self.master.update()
        self.lbl_team1.place(x = (60+(180+120)/2-self.lbl_team1.winfo_reqwidth()/2), y = 0)

        self.lbl_score = Label(self.master, text = match[3], font=(None, 14))
        self.master.update()
        self.lbl_score.place(x = (60+180+120+(70)/2-self.lbl_score.winfo_reqwidth()/2), y = 0)

        self.lbl_team2 = Label(self.master, text = match[4], font=(None, 14))
        self.master.update()
        self.lbl_team2.place(x = (60+180+120+70+(120+180)/2-self.lbl_team2.winfo_reqwidth()/2), y = 0)

        if type == 1:
            self.btn_addGoal = Button(self.master, text = "Add goal", width = 10, height = 2, command = partial(self.addEvent, match, 0, self.master))
            self.btn_addGoal.place(x = 10, y = 30)

            self.btn_addTag = Button(self.master, text = "Add tag", width = 10, height = 2, command = partial(self.addEvent, match, 1, self.master))
            self.btn_addTag.place(x = 100, y = 30)

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
            self.master.grid_rowconfigure(row, minsize = 35)

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
            self.txt_time.config(state = 'disabled')
            self.txt_time.config(state = 'readonly')

    def add(self):
        pass
    def cancel(self):
        self.master.destroy()
        windowsGlo.remove(self.master)

# class adminGUI:
#     def __init__(self, master, services):
#         windowsGlo.append(master)
#         self.master = master
#         self.services = services
#         self.master.title("Administrator")
#         # self.master.resizable(0, 0)
#         self.master.focus()
#         self.master.grab_set()
#         self.master['padx'] = 10
#         self.master['pady'] = 10

#         self.btn_edit = Button(self.master, text = "Edit", command = partial(self.edit, self.master))
#         self.btn_edit.grid(column = 0, row = 0, sticky = tk.W, padx = 0, pady = 0, ipadx = 20, ipady = 10)

#         self.lbl_title = Label(self.master, text = 'Match List', font=("Helvetica", 16))
#         self.lbl_title.grid(row = 0, column = 1, sticky = NS)

#         self.btn_logout = Button(self.master, text = "Log out")
#         self.btn_logout.grid(column = 2, row = 0, sticky = tk.E, padx = 0, pady = 0, ipadx = 20, ipady = 10)

#         # columns
#         columns = ('#1', '#2', '#3', '#4', '#5')
#         self.tree = ttk.Treeview(self.master, columns = columns, show = 'headings', height = 20)

#         #config column width
#         self.tree.column("#1", anchor = 'center', minwidth = 50, width = 50)
#         self.tree.column("#2", anchor = 'center', minwidth = 50, width = 100)
#         self.tree.column("#3", anchor = 'center', minwidth = 50, width = 100)
#         self.tree.column("#4", anchor = 'center', minwidth = 50, width = 50)
#         self.tree.column("#5", anchor = 'center', minwidth = 50, width = 100)

#         # define headings
#         self.tree.heading('#1', text='ID')
#         self.tree.heading('#2', text='Time')
#         self.tree.heading('#3', text='Team 1')
#         self.tree.heading('#4', text='Score')
#         self.tree.heading('#5', text='Team 2')

#         self.tree.grid(row = 1, column = 0, padx = 0, pady = 5, columnspan = 3, sticky='nsew')

#         # add a scrollbar
#         self.scrollbar = ttk.Scrollbar(self.master, orient = tk.VERTICAL, command = self.tree.yview)
#         self.tree.configure(yscroll = self.scrollbar.set)
#         self.scrollbar.grid(row = 1, column = 3, padx = 0, pady = 5, sticky = 'ns')

#         # add data
#         contacts = []
#         contacts.append(('1', '22:10', 'Verona', '1 - 1', 'Bologna'))

#         for contact in contacts:
#             self.tree.insert('', tk.END, values=contact)
        
#         self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

#         self.btn_add = Button(self.master, text = "Add match")
#         self.btn_add.grid(column = 0, row = 2, sticky = tk.E, padx = 0, pady = 0, ipadx = 10, ipady = 5)

#         self.btn_delete = Button(self.master, text = "Delete match")
#         self.btn_delete.grid(column = 2, row = 2, sticky = tk.W, padx = 0, pady = 0, ipadx = 10, ipady = 5)

#     def on_closing(self):
#         self.master.destroy()
#         windowsGlo.remove(self.master)

#     def edit(self, parent):
#         match = self.tree.item(self.tree.focus())['values']
#         if match == '':
#             return

#         window_edit = Toplevel(self.master)
#         editGUI(window_edit, parent, self.services, match)
#         center(window_edit)
#         window_edit.mainloop()

# class editGUI:
#     def __init__(self, master, parent, services, match):
#         windowsGlo.append(master)
#         self.services = services
#         self.master = master
#         self.master.title("Edit match")
#         # self.master.resizable(0, 0)
#         self.master.focus()
#         self.master.grab_set()
#         self.master['padx'] = 10
#         self.master['pady'] = 10

#         self.parent = parent

#         # self.lbl_ID = Label(self.master, text = match[0], font=("Helvetica", 14))
#         # self.lbl_ID.grid(row = 0, column = 0)

#         self.lbl_time = Label(self.master, text = match[1])
#         self.lbl_time.grid(row = 0, column = 0)

#         self.lbl_team1 = Label(self.master, text = match[2], font=("Helvetica", 14))
#         self.lbl_team1.grid(row = 0, column = 1)

#         self.lbl_score = Label(self.master, text = match[3], font=("Helvetica", 14))
#         self.lbl_score.grid(row = 0, column = 2)

#         self.lbl_team2 = Label(self.master, text = match[4], font=("Helvetica", 14))
#         self.lbl_team2.grid(row = 0, column = 3)

#         # columns
#         columns = ('#1', '#2', '#3', '#4', '#5', '#6')
#         self.tree = ttk.Treeview(self.master, columns = columns, show = 'headings', height = 20)

#         #config column width
#         self.tree.column("#1", anchor = 'center', minwidth = 50, width = 50)
#         self.tree.column("#2", anchor = 'center', minwidth = 50, width = 100)
#         self.tree.column("#3", anchor = 'center', minwidth = 50, width = 100)
#         self.tree.column("#4", anchor = 'center', minwidth = 50, width = 50)
#         self.tree.column("#5", anchor = 'center', minwidth = 50, width = 100)
#         self.tree.column("#6", anchor = 'center', minwidth = 50, width = 100)

#         # define headings
#         self.tree.heading('#1', text='Time')
#         self.tree.heading('#2', text='Team 1 player')
#         self.tree.heading('#3', text='Event')
#         self.tree.heading('#4', text='Score')
#         self.tree.heading('#5', text='Event')
#         self.tree.heading('#6', text='Team 2 player')

#         self.tree.grid(row = 1, column = 0, padx = 0, pady = 5, columnspan = 4, sticky='nsew')

#         # add a scrollbar
#         self.scrollbar = ttk.Scrollbar(self.master, orient = tk.VERTICAL, command = self.tree.yview)
#         self.tree.configure(yscroll = self.scrollbar.set)
#         self.scrollbar.grid(row = 1, column = 4, padx = 0, pady = 5, sticky = 'ns')

#         self.btn_addGoal = Button(self.master, text = "Add goal")
#         self.btn_addGoal.grid(column = 1, row = 2, padx = 0, pady = 0, ipadx = 10, ipady = 5)

#         self.btn_addTag = Button(self.master, text = "Add tag")
#         self.btn_addTag.grid(column = 2, row = 2, padx = 0, pady = 0, ipadx = 10, ipady = 5)

#         # add data
#         contacts = []
#         contacts.append(("10'", 'A', 'Score', '1 - 0', '', ''))
#         contacts.append(("20'", '', '', '1 - 1', 'Score', 'B'))

#         for contact in contacts:
#             self.tree.insert('', tk.END, values=contact)

#         self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

#     def on_closing(self):
#         self.master.destroy()
#         self.parent.focus()
#         self.parent.grab_set()
#         windowsGlo.remove(self.master)

window_client = Tk()
ClientGUI(window_client)
center(window_client)
window_client.mainloop()