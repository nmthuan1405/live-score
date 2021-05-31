from cgitb import text
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

timeout = 2000
windowsDetail = None

class ClientGUI:
    def __init__(self, master):
        master.report_callback_exception = self.report_callback_exception

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

        if windowsDetail:
            windowsDetail.destroy()
            self.master.deiconify()
        
        self.txt_IP_input.config(state = 'normal')
        self.btn_connect.config(text = 'Connect')
        self.txt_User.config(state = 'disabled')
        self.txt_Password.config(state = 'disabled')
        self.btn_SignUp.config(state = 'disabled')
        self.btn_SignIn.config(state = 'disabled')
        self.txt_IP_input.focus()

        showerror(title = 'Error', message = 'Lost connection', parent = self.master)

    def connect(self):
        if self.services == None:
            try:
                self.services = client.Client(self.txt_IP_input.get())
                self.services.connect()
                self.services.s_ping()
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
        User = self.txt_User.get()
        Pass = self.txt_Password.get()
        if User == '' or Pass == '':
            showerror('Error', 'Invalid value', parent = self.master)
            return

        check = self.services.s_auth(User, Pass, 'signUp')
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
        global windowsDetail
        windowsDetail = window_user
        userGUI(window_user, self.master, self.services)
        window_user.mainloop()

    def exit(self):
        if self.services != None:
            if not askokcancel("Exit", "Client is connecting.\nDo you want to disconnect?"):
                return
            try:
                self.services.s_close()
            except:
                pass
            
        self.master.destroy()

class userGUI:
    def __init__(self, master, parent, services):
        self.master = master
        self.parent = parent
        self.services = services

        self.parent.withdraw()

        if self.services.isAdmin:
            self.master.title("Administrator")
        else:
            self.master.title("User")
        self.master.resizable(0, 0)


        self.master.focus()
        self.master.grab_set()
        self.master['padx'] = 10
        self.master['pady'] = 10

        self.lbl_date = Label(self.master, text='Choose date:')
        self.lbl_date.place(x = 0, y = 0)

        self.txt_date = DateEntry(self.master, width=12, background='gray', foreground='white', borderwidth=2)
        self.txt_date.config(state = 'disabled')
        self.txt_date.place(x = 80, y = 0)

        self.isCheck = tk.IntVar()
        self.allDate = tk.Checkbutton(self.master, text = 'All Date', variable = self.isCheck, onvalue = 1, offvalue = 0, command = self.checker)
        self.allDate.select()
        self.allDate.place(x = 180, y = 0)

        self.lbl_load = Label(self.master, text='Loading...')
        self.lbl_load.place(x = 280, y = 2)

        if self.services.isAdmin:
            self.btn_edit = Button(self.master, text = "Edit match", width = 12, height = 1, command = self.edit)
            self.btn_edit.grid(column = 1, row = 1, sticky = tk.W, padx = 0, pady = 0, ipady = 0)

            self.btn_add = Button(self.master, text = "Add match", width = 12, height = 1, command = self.addMatch)
            self.btn_add.grid(column = 2, row = 1, sticky = tk.W, padx = 0, pady = 0, ipady = 0)

            self.btn_delete = Button(self.master, text = "Delete match", width = 12, height = 1, command = self.delete)
            self.btn_delete.grid(column = 3, row = 1, sticky = tk.W, padx = 0, pady = 0, ipady = 0)

            self.btn_editAccount = Button(self.master, text = "Edit account", width = 12, height = 1, command = self.editAccount)
            self.btn_editAccount.grid(column = 5, row = 1, sticky = tk.E, padx = 0, pady = 0, ipady = 0)

        self.btn_detail = Button(self.master, text = "Match detail", width = 12, height = 1, command = self.detail)
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
        self.tree["displaycolumns"]=("1", "2", "3", "4")
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

        def dateChanged(event):
            selectedDate = self.txt_date.get_date()
            self.allDate.deselect()

            self.services.update.details['main'][0] = str(self.txt_date.get_date())

        self.txt_date.bind('<<DateEntrySelected>>', dateChanged)

        self.master.update_idletasks()

        # start init
        self.services.req.start()
        self.services.update.addWindows('main', False)
        self.services.update.setTimeout(timeout)
        self.services.update.start()
        self.schedule()

    def checker(self):
        if self.isCheck.get() == 0:
            self.txt_date.config(state = 'normal')
            self.services.update.details['main'][0] = str(self.txt_date.get_date())
        if self.isCheck.get() == 1:
            self.txt_date.config(state = 'disabled')
            self.services.update.details['main'][0] = False
                

    def schedule(self):
        matches = self.services.update.details['main'][1]
        if matches is not None:
            if matches != False:
                choosen = self.tree.item(self.tree.focus())['values']
                for row in self.tree.get_children():
                    self.tree.delete(row)
                    
                for match in matches:
                    self.tree.insert('', tk.END, values = match)

                if choosen != '':
                    id = None
                    for row in self.tree.get_children():
                        if self.tree.item(row)['values'][0] == choosen[0]:
                            id = row
                            break

                    if id is not None: 
                        self.tree.selection_set(id)   
                        self.tree.focus(id)

                self.lbl_load.config(text = '')
            else:
                showerror('Error', 'Unable to fetch data', parent = self.master)
                return

        self.master.after(timeout, self.schedule)


    def detail(self):
        match = self.tree.item(self.tree.focus())['values']
        if match == '':
            showwarning("Warning", "Choose a match to see detail", parent = self.master)
            return

        if match[0] in [*self.services.update.details]:
            showinfo('Oops', 'You have already opened this match', parent = self.master)
            return

        window_detail = Toplevel(self.master)
        detailGUI(window_detail, self.master, self.services, match[0])
        window_detail.mainloop()


    def edit(self):
        match = self.tree.item(self.tree.focus())['values']
        if match == '':
            showwarning("Warning", "Choose a match to edit", parent = self.master)
            return

        window_edit = Toplevel(self.master)
        addMatchGUI(window_edit, self.master, self.services, match[0])
        window_edit.mainloop()

    def addMatch(self):
        window_addMatch = Toplevel(self.master)
        addMatchGUI(window_addMatch, self.master, self.services)
        window_addMatch.mainloop()

    def delete(self):
        match = self.tree.item(self.tree.focus())['values']
        if match == '':
            showwarning("Warning", "Choose a match to delete", parent = self.master)
            return

        if self.services.req.command('delMatch', match[0]):
            showinfo('Success', 'Delete match successfully', parent = self.master)
        else:
            showerror('Error', 'Unable to delete match', parent = self.master)        

    def editAccount(self):
        window_editAccount = Toplevel(self.master)
        editAccountGUI(window_editAccount, self.master, self.services)
        window_editAccount.mainloop()

    def signOut(self):
        self.services.update.stop()
        self.services.req.stop()
        self.services.s_signOut()


        self.master.destroy()

        global windowsDetail
        windowsDetail = None
        self.parent.deiconify()

class detailGUI:
    def __init__(self, master, parent, services, match):
        self.master = master
        self.parent = parent

        self.services = services 
        self.match = match
        self.master.title("Match details")
        self.master.resizable(0, 0)
        self.master.focus()
        # self.master.grab_set()    # Bo lock parent GUI
        self.master['padx'] = 10
        self.master['pady'] = 10

        self.lbl_ID = Label(self.master)
        self.lbl_ID.config(text = match)

        self.lbl_time = Label(self.master)
        self.lbl_time.config(text = 'Loading...')

        self.lbl_currTime = Label(self.master, font=(None, 18))     # phut hien tai cua tran dau

        self.lbl_team1 = Label(self.master, font=(None, 14), anchor = tk.CENTER, width = 27)

        self.lbl_score = Label(self.master, font=(None, 14), anchor = tk.CENTER, width = 6)

        self.lbl_team2 = Label(self.master, font=(None, 14), anchor = tk.CENTER, width = 27)

        if self.services.isAdmin:
            self.btn_addEvent = Button(self.master, text = "Add event", width = 10, height = 1, command =self.addEvent)
            self.btn_addEvent.place(x = 10, y = 0)

            self.btn_editEvent = Button(self.master, text = "Edit event", width = 10, height = 1, command = self.editEvent)
            self.btn_editEvent.place(x = 110, y = 0)

            self.btn_deleteEvent = Button(self.master, text = "Delete event", width = 10, height = 1, command = self.deleteEvent)
            self.btn_deleteEvent.place(x = 210, y = 0)

            self.isCheck = tk.IntVar()
            self.checkbox = tk.Checkbutton(self.master, text = 'Show all event', variable = self.isCheck, onvalue = 1, offvalue = 0, command = self.checker)
            self.checkbox.select()
            self.checkbox.place(x = 310, y = 0)

            self.lbl_ID.place(x = 10, y = 30)
            self.lbl_time.place( x = 10, y = 50)
            self.lbl_currTime.place(x = 650, y = 30)
            self.master.update()
            self.lbl_team1.place(x = 60, y = 65)
            self.master.update()
            self.lbl_score.place(x = 60+180+120, y = 65)
            self.master.update()
            self.lbl_team2.place(x = 60+180+120+70, y = 65)
        else:
            self.lbl_ID.place(x = 10, y = 0)
            self.lbl_time.place( x = 10, y = 20)
            self.lbl_currTime.place(x = 600, y = 0)
            self.master.update()
            self.lbl_team1.place(x = 60, y = 35)
            self.master.update()
            self.lbl_score.place(x = 60+180+120, y = 35)
            self.master.update()
            self.lbl_team2.place(x = 60+180+120+70, y = 35)

        # columns
        columns = ('#1', '#2', '#3', '#4', '#5', '#6', '#7')
        self.tree = ttk.Treeview(self.master, columns = columns, show = 'headings', height = 20)

        #config column width
        self.tree.column("#1", anchor = 'center', minwidth = 0, width = 0)
        self.tree.column("#2", anchor = 'center', minwidth = 50, width = 60)
        self.tree.column("#3", anchor = 'center', minwidth = 50, width = 180)
        self.tree.column("#4", anchor = 'center', minwidth = 50, width = 120)
        self.tree.column("#5", anchor = 'center', minwidth = 50, width = 70)
        self.tree.column("#6", anchor = 'center', minwidth = 50, width = 120)
        self.tree.column("#7", anchor = 'center', minwidth = 50, width = 180)

        # define headings
        self.tree.heading('#1', text='ID')
        self.tree.heading('#2', text='Time')
        self.tree.heading('#3', text='Team 1 player')
        self.tree.heading('#4', text='Event')
        self.tree.heading('#5', text='Score')
        self.tree.heading('#6', text='Event')
        self.tree.heading('#7', text='Team 2 player')
        self.tree["displaycolumns"]=("1", "2", "3", "4", "5", "6")

        if self.services.isAdmin:
            self.tree.grid(row = 3, column = 0, padx = 0, pady = 5, columnspan = 5, sticky='nsew')
        else:
            self.tree.grid(row = 2, column = 0, padx = 0, pady = 5, columnspan = 5, sticky='nsew')

        # add a scrollbar
        self.scrollbar = ttk.Scrollbar(self.master, orient = tk.VERTICAL, command = self.tree.yview)
        self.tree.configure(yscroll = self.scrollbar.set)
        if self.services.isAdmin:
            self.scrollbar.grid(row = 3, column = 5, padx = 0, pady = 5, sticky = 'ns')
        else:
            self.scrollbar.grid(row = 2, column = 5, padx = 0, pady = 5, sticky = 'ns')

        col_count, row_count = self.master.grid_size()
        for col in range(col_count):
            self.master.grid_columnconfigure(col, minsize = 0)
        
        for row in range(row_count):
            self.master.grid_rowconfigure(row, minsize = 30)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.master.update_idletasks()

        # init
        self.services.update.addWindows(self.match, not self.services.isAdmin)
        self.schedule()


    def schedule(self):
        details = self.services.update.details[self.match][1]
        if details is not None:
            if details:
                match, rows = details
                id, timeStamp, time, team1Name, team2Name, score, timeInt = match
                self.lbl_ID.config(text = id)
                self.lbl_time.config(text = timeStamp)
                self.lbl_team1.config(text = team1Name)
                self.lbl_team2.config(text = team2Name)
                self.lbl_score.config(text = score)
                self.lbl_currTime.config(text = time)

                if rows is not None:
                    choosen = self.tree.item(self.tree.focus())['values']
                    for row in self.tree.get_children():
                        self.tree.delete(row)

                    for row in rows:
                        self.tree.insert('', tk.END, values = row)

                    if choosen != '':
                        id = None
                        for row in self.tree.get_children():
                            if self.tree.item(row)['values'][0] == choosen[0]:
                                id = row
                                break

                        if id is not None: 
                            self.tree.selection_set(id)   
                            self.tree.focus(id)
            else:
                showerror('Error', 'Unable to fetch data')
                self.on_closing()
                return

        self.master.after(timeout, self.schedule)

    def on_closing(self):
        self.services.update.removeWindows(self.match)

        self.master.destroy()
        self.parent.focus()
        self.parent.grab_set()

    def addEvent(self):
        window_addEvent = Toplevel(self.master)
        addEventGUI(window_addEvent, self.master, self.services, self.match, None)
        window_addEvent.mainloop()

    def editEvent(self):
        event = self.tree.item(self.tree.focus())['values']
        if event == '':
            showwarning("Warning", "Choose an event to edit", parent = self.master)
            return

        window_editEvent = Toplevel(self.master)
        addEventGUI(window_editEvent, self.master, self.services, self.match, event[0])
        window_editEvent.mainloop()

    def deleteEvent(self):
        event = self.tree.item(self.tree.focus())['values']
        if event == '':
            showwarning("Warning", "Choose an event to delete", parent = self.master)
            return

        if self.services.req.command('delDetail', event[0]):
            showinfo('Success', 'Delete event successfully', parent = self.master)
        else:
            showerror('Error', 'Unable to delete match', parent = self.master)  

    def checker(self):
        if self.isCheck.get() ==  1:
            self.services.update.details[self.match][0] = False
        else:
            self.services.update.details[self.match][0] = True


class addEventGUI:
    def __init__(self, master, parent, services, match, event):
        self.services = services
        self.match = match
        self.event = event

        self.master = master
        self.parent = parent

        if event is None:
            self.master.title("Add event")
        else:
            self.master.title("Edit event")
        self.master.resizable(0, 0)
        self.master.focus()
        self.master.grab_set()
        self.master['padx'] = 10
        self.master['pady'] = 10

        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)
        self.master.columnconfigure(2, weight=1)

        self.lbl_event = Label(self.master, text = 'Choose event')
        self.lbl_event.grid(column = 0, row = 3, sticky = W)

        self.eventTypes = ('Goal', 'Yellow card', 'Red card', 'Half-time break', 'Stoppage time')
        self.selected_eventType = tk.StringVar()
        self.cbb_eventType = ttk.Combobox(self.master, textvariable = self.selected_eventType)
        self.cbb_eventType['values'] = self.eventTypes
        if event is None:
            self.cbb_eventType.current(0)

        self.cbb_eventType['state'] = 'readonly'  # normal
        self.cbb_eventType.grid(column = 0, row = 4, columnspan = 3, sticky = EW)

        def eventTypeChanged(event):
            if(self.cbb_eventType.get() == self.eventTypes[0] or self.cbb_eventType.get() == self.eventTypes[1] or self.cbb_eventType.get() == self.eventTypes[2]):
                self.lbl_team.grid(column = 0, row = 5, sticky = W)
                self.cbb_team.grid(column = 0, row = 6, columnspan = 3, sticky = EW, padx = 0, pady = 0)

                self.lbl_player.grid(column = 0, row = 7, sticky = W)
                self.txt_player.grid(column = 0, row = 8, columnspan = 3, sticky = EW, padx = 0, pady = 0)

                self.lbl_duration.grid_remove()
                self.spinDur.grid_remove()
                self.lbl_min.grid_remove()
                self.txt_time.config(state = 'normal')
                self.txt_time.delete(0, 'end')

            if(self.cbb_eventType.get() == self.eventTypes[3]):
                self.lbl_team.grid_remove()
                self.cbb_team.grid_remove()

                self.lbl_player.grid_remove()
                self.txt_player.grid_remove()

                self.lbl_duration.grid(column = 0, row = 6, sticky = W)
                self.spinDur.set(15)
                self.spinDur.grid(row = 7, column = 0, columnspan = 1, sticky = W)
                self.lbl_min.grid(row = 7, column = 1, sticky = W)
                self.txt_time.config(state = 'normal')
                self.txt_time.delete(0, 'end')

            if(self.cbb_eventType.get() == self.eventTypes[4]):
                self.lbl_team.grid_remove()
                self.cbb_team.grid_remove()

                self.lbl_player.grid_remove()
                self.txt_player.grid_remove()

                self.lbl_duration.grid(column = 0, row = 6, sticky = W)
                self.spinDur.set(5)
                self.spinDur.grid(row = 7, column = 0, columnspan = 1, sticky = W)
                self.lbl_min.grid(row = 7, column = 1, sticky = W)
                self.txt_time.delete(0, 'end')
                self.txt_time.insert(0, '90')
                self.txt_time.config(state = 'disable')
        
        self.cbb_eventType.bind('<<ComboboxSelected>>', eventTypeChanged)

        self.lbl_ID = Label(self.master, text = 'Event ID')
        self.lbl_ID.grid(column = 0, row = 0, sticky = W)

        self.txt_ID = Entry(self.master)
        if event is None:
            self.txt_ID.insert(-1, uuid.uuid4().hex)
        else:
            self.txt_ID.insert(-1, event)
        self.txt_ID.config(state = 'readonly')
        self.txt_ID.grid(column = 0, row = 1, columnspan = 3, sticky = EW, padx = 0)

        self.lbl_team = Label(self.master, text = 'Team')
        self.teams = self.services.update.details[self.match][1][0][3:5]
        self.selected_team = tk.StringVar()
        self.cbb_team = ttk.Combobox(self.master, textvariable = self.selected_team)
        self.cbb_team['values'] = self.teams
        self.cbb_team.current(0)
        self.cbb_team['state'] = 'readonly'  # normal

        self.lbl_player = Label(self.master, text = 'Player')
        self.txt_player = Entry(self.master)

        if event is None:
            self.lbl_team.grid(column = 0, row = 5, sticky = W)
            self.cbb_team.grid(column = 0, row = 6, columnspan = 3, sticky = EW, padx = 0, pady = 0)

            self.lbl_player.grid(column = 0, row = 7, sticky = W)
            self.txt_player.grid(column = 0, row = 8, columnspan = 3, sticky = EW, padx = 0, pady = 0)

        self.lbl_time = Label(self.master, text = 'Time')
        self.lbl_time.grid(column = 0, row = 9, sticky = W)

        self.txt_time = Entry(self.master)
        
        self.txt_time.grid(column = 0, row = 10, columnspan = 3, sticky = EW, padx = 0, pady = 0)

        self.lbl_duration = Label(self.master, text = 'Duration')

        self.currDur = tk.IntVar(value = 15)
        self.spinDur = ttk.Spinbox(self.master, width = 8, from_=0, to=30, textvariable=self.currDur, wrap=True)

        self.lbl_min = Label(self.master, text = 'minutes')

        if event is None:
            self.btn_add = Button(self.master, text="Add", command = self.add, width = 8)
            self.btn_add.grid(row = 12, column = 1, sticky = tk.SW, padx = 0, pady = 0, ipadx = 0)
        else:
            self.btn_change = Button(self.master, text="Edit", command = self.change, width = 8)
            self.btn_change.grid(row = 12, column = 1, sticky = tk.SW, padx = 0, pady = 0, ipadx = 0)

        self.btn_cancel = Button(self.master, text="Cancel", command = self.cancel, width = 8)
        self.btn_cancel.grid(row = 12, column = 2, sticky = tk.SE, padx = 0, pady = 0, ipadx = 0)


        col_count, row_count = self.master.grid_size()
        for col in range(col_count):
            self.master.grid_columnconfigure(col, minsize = 70)
        for row in range(row_count):
            self.master.grid_rowconfigure(row, minsize = 22)

        self.master.update_idletasks()

        if event is not None:
            data = self.services.req.command('getDetail', event)

            if data and len(data) == 1:
                data = data[0]

                self.cbb_eventType.current(data[3] - 1)
                eventTypeChanged(None)

                self.txt_time.insert(-1, data[2])
                if data[3] == 4 or data[3] == 5:
                    self.spinDur.delete(0, END)
                    self.spinDur.insert(-1, data[4])
                else:
                    self.cbb_team.current(data[4])
                    self.txt_player.insert(-1, data[5])
                
    def checker(self):
        if self.isCheck.get() == 0:
            self.txt_time.config(state = 'normal')
            self.txt_time.delete(0, END)
        if self.isCheck.get() == 1:
            self.txt_time.delete(0, END)
            self.txt_time.insert(-1, 'now')
            self.txt_time.config(state = 'readonly')

    def checkData(self, id, code, time, team, player):
        if (not time.isdigit()) or int(time) < 0:
            return False
        if code == '4' or code == '5':
            if (not team.isdigit()) or int(team) < 0:
                return False
        else:
            if player == '':
                return False
        return True

    def getData(self):
        id = self.txt_ID.get()
        time = self.txt_time.get()
        code = client.eventNameToCode(self.cbb_eventType.get())

        if code == '4' or code == '5':
            team = self.spinDur.get()
            player = ''
        else:
            team = self.teams.index(self.cbb_team.get())
            player = self.txt_player.get()

        return id, code, time, team, player

    def add(self):
        id, code, time, team, player = self.getData()
        if self.checkData(id, code, time, team, player):
            if self.services.req.command('insertDetail', (id, self.services.update.details[self.match][1][0][0], code, team, player, time)):
                self.cancel()
                showinfo('Success', 'Add event successfully', parent = self.parent)
            else:
                showerror('Error', 'Unable to add this event', parent = self.master)
        else:
            showerror('Error', 'Invalid data', parent = self.master)
        
    def change(self):
        id, code, time, team, player = self.getData()
        if self.checkData(id, code, time, team, player):
            if self.services.req.command('editDetail', (id, code, team, player, time)):
                self.cancel()
                showinfo('Success', 'Edit event successfully', parent = self.parent)
            else:
                showerror('Error', 'Unable to edit this event', parent = self.master)
        else:
            showerror('Error', 'Invalid data', parent = self.master)

    def cancel(self):
        self.master.destroy()

class addMatchGUI:
    def __init__(self, master, parent, services, match = None):
        self.services = services
        self.master = master
        self.parent = parent

        if match is None:
            self.master.title("Add match")
        else:
            self.master.title("Edit match")
        self.master.resizable(0, 0)
        self.master.focus()
        self.master.grab_set()
        self.master['padx'] = 10
        self.master['pady'] = 10

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
            self.txt_ID.config(state = 'readonly')
        else:
            self.txt_ID.grid(row = 1, column = 0, columnspan = 2, sticky = EW, padx = 0)
            self.isCheck = tk.IntVar()
            self.isDefault = tk.Checkbutton(self.master, text = 'Default', variable = self.isCheck, onvalue = 1, offvalue = 0, command = self.checker)
            self.isDefault.select()

            self.txt_ID.insert(-1, uuid.uuid4().hex)
            self.txt_ID.config(state = 'readonly')

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

        self.master.update_idletasks()

        if match is not None:
            data = self.services.req.command('getMatch', match)
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
        self.parent.focus()
        self.parent.grab_set()

    def checker(self):
        if self.isCheck.get() == 0:
            self.txt_ID.config(state = 'normal')
            self.txt_ID.delete(0, END)
        if self.isCheck.get() == 1:
            self.txt_ID.delete(0, END)
            self.txt_ID.insert(-1, uuid.uuid4().hex)
            self.txt_ID.config(state = 'readonly')

    def getData(self):
        id = self.txt_ID.get()
        team1 = self.txt_team1.get()
        team2 = self.txt_team2.get()
        hour = self.spinHour.get()
        min = self.spinMin.get()

        return id, team1, team2, hour, min

    def checkData(self, team1, team2, hour, min):
        if team1 == '' or team2 == '' or team1 == team2:
            return False 
        if (not hour.isdigit()) or int(hour) < 0 or int(hour) > 23:
            return False
        if (not min.isdigit()) or int(min) < 0 or int(min) > 59:
            return False

        return True 

    def change(self):
        id, team1, team2, hour, min = self.getData()
        if self.checkData(team1, team2, hour, min):
            time = str(self.txt_date.get_date()) + ' ' + hour.zfill(2) + ':' + min.zfill(2)
            if self.services.req.command('editMatch', (id, team1, team2, time)):
                self.on_closing()
                showinfo('Success', 'Change match\'s information successfully', parent = self.parent)
            else:
                showerror('Error', 'Unable to change match\'s information', parent = self.master)
        else:
            showerror('Error', 'Invalid data', parent = self.master)

    def add(self):
        id, team1, team2, hour, min = self.getData()
        if self.checkData(team1, team2, hour, min):
            time = str(self.txt_date.get_date()) + ' ' + hour.zfill(2) + ':' + min.zfill(2)
            if self.services.req.command('addMatch', (id, team1, team2, time)):
                self.on_closing()
                showinfo('Success', 'Add match successfully', parent = self.parent)
            else:
                showerror('Error', 'Unable to create a new match', parent = self.master)
        else:
            showerror('Error', 'Invalid data', parent = self.master)


class editAccountGUI:
    def __init__(self, master, parent, services):
        self.services = services
        self.master = master
        self.master.title("Edit account")
        self.master.resizable(0, 0)
        self.master.focus()
        self.master.grab_set()
        self.master['padx'] = 10
        self.master['pady'] = 10

        self.parent = parent

        self.btn_edit = Button(self.master, text="Edit", command = self.edit, width = 20)
        self.btn_edit.grid(row = 0, column = 1, sticky = tk.W, padx = 0, pady = 0, ipadx = 0)

        self.btn_add = Button(self.master, text="Add", command = self.add, width = 20)
        self.btn_add.grid(row = 0, column = 0, padx = 0, pady = 0, ipadx = 0)

        self.btn_delete = Button(self.master, text="Delete", command = self.delete, width = 20)
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
        
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.master.update_idletasks()

        self.schedule()

    def schedule(self):
        listAccount = self.services.req.command('accountList')

        choosen = self.tree.item(self.tree.focus())['values']
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        for account in listAccount:
            self.tree.insert('', tk.END, values = account)

        if choosen != '':
            id = None
            for row in self.tree.get_children():
                if self.tree.item(row)['values'][0] == choosen[0]:
                    id = row
                    break

            if id is not None: 
                self.tree.selection_set(id)   
                self.tree.focus(id)

        self.master.after(timeout, self.schedule)

    def edit(self):
        account = self.tree.item(self.tree.focus())['values']
        if account == '':
            showwarning('Warning', 'Please choose account to edit', parent = self.master)
            return

        window_edit = Toplevel(self.master)
        editGUI(window_edit, self.master, self.services, account)
        window_edit.mainloop()

    def add(self):
        window_add = Toplevel(self.master)
        editGUI(window_add, self.master, self.services, None)
        window_add.mainloop()

    def delete(self):
        account = self.tree.item(self.tree.focus())['values']
        if account == '':
            showwarning('Warning', 'Please choose account to delete', parent = self.master)
            return
        
        if self.services.req.command('delAccount', account[0]):
            showinfo('Sucess', 'Delete this account successfully', parent = self.master)
        else:
            showerror('Error', 'Unable to delete this account', parent = self.master)

    def on_closing(self):
        self.master.destroy()
        self.parent.focus()
        self.parent.grab_set()

class editGUI:
    def __init__(self, master, parent, services, account):
        self.services = services
        self.master = master
        if account is not None:
            self.master.title("Edit Account")
        else:
            self.master.title("Add Account")
        self.master.resizable(0, 0)
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
            if account[2] == 1:
                self.isAdmin.select()

            self.txt_user.config(state = 'readonly')

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

    def getData(self):
        User = self.txt_user.get()
        Pass = self.txt_pass.get()
        isAdmin = self.isCheck.get()

        return User, Pass, isAdmin

    def checkData(self, User, Pass):
        if User == '' or Pass == '':
            return False
        return True

    def change(self):
        User, Pass, isAdmin = self.getData()
        if self.checkData(User, Pass):
            if self.services.req.command('editAccount', (User, Pass, isAdmin)):
                self.on_closing()
                showinfo('Success', 'Change account password successfully', parent = self.parent)
            else:
                showerror('Error', 'Unable to edit account', parent = self.master)
        else:
            showerror('Error', 'Invalid data', parent = self.master)

    def add(self):
        User, Pass, isAdmin = self.getData()
        if self.checkData(User, Pass):
            if self.services.req.command('signUp', (User, Pass, isAdmin)):
                self.on_closing()
                showinfo('Success', 'Create account successfully', parent = self.parent)
            else:
                showerror('Error', 'Unable to create account', parent = self.master)
        else:
            showerror('Error', 'Invalid data', parent = self.master)

    def cancel(self):
        self.on_closing()


window_client = Tk()
ClientGUI(window_client)
window_client.eval('tk::PlaceWindow . center')
window_client.mainloop()