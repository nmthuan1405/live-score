import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.messagebox import showerror, showinfo, askokcancel
from tkinter import scrolledtext
from functools import partial

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

        self.lbl_Title = Label(self.master, text = "LIVE SCORE", font=("Helvetica", 14))
        self.lbl_Title.grid(column = 0, row = 0, columnspan = 3, sticky = tk.N, padx = 0, pady = 0)

        self.lbl_IPInput = Label(self.master, text = "Server IP")
        self.lbl_IPInput.grid(column = 0, row = 1, sticky = tk.W, padx = 0, pady = 0)

        self.txt_IP_input = Entry(self.master)
        self.txt_IP_input.insert(-1, 'localhost')
        self.txt_IP_input.focus()
        self.txt_IP_input.grid(column = 0, row = 2, columnspan = 2, sticky = EW, padx = 0)

        self.btn_connect = Button(self.master, text="Connect", command = self.connect)
        self.btn_connect.grid(column=2, row=2, sticky = tk.E, padx = 0, pady = 0, ipadx = 10)
        self.master.bind('<Return>', self.callback)

        self.lbl_User = Label(self.master, text = "Username")
        self.lbl_User.grid(column = 0, row = 4, sticky = tk.W, padx = 0, pady = 0)

        self.txt_User = Entry(self.master)
        self.txt_User.grid(column = 0, row = 5, columnspan = 3, sticky = EW)

        self.lbl_Password = Label(self.master, text = "Password")
        self.lbl_Password.grid(column = 0, row = 6, sticky = tk.W, padx = 0, pady = 0)

        self.txt_Password = Entry(self.master)
        self.txt_Password.grid(column = 0, row = 7, columnspan = 3, sticky = EW)

        self.btn_SignUp = Button(self.master, text="Sign Up", command = self.signUp)
        self.btn_SignUp.grid(column=0, row=9, rowspan = 2, sticky = tk.SW, padx = 0, pady = 0, ipadx = 10)

        self.btn_SignIn = Button(self.master, text="Sign In", command = self.signIn)
        self.btn_SignIn.grid(column=1, row=9, rowspan = 2, sticky = tk.SW, padx = 0, pady = 0, ipadx = 10)

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
        for windows in windowsGlo:
            windows.destroy()

        self.txt_IP_input.config(state = 'normal')
        self.btn_connect.config(text = 'Connect')
        # showerror(title = 'Error', message = 'Lost connection')

    def connect(self):
        pass
        # if self.services == None:
        #     try:
        #         self.services = client.ClientServices(self.txt_IP_input.get())
        #         self.services.connectServer()
        #     except:
        #         showerror(title = 'Error', message = 'Cannot connect to server.', parent = self.master)
        #         self.services = None
        #     else:
        #         self.txt_IP_input.config(state = 'disabled')
        #         self.btn_connect.config(text = 'Disconnect')
        #         showinfo("Sucess", "Connect to server sucessfully", parent = self.master)
        
        # else:
        #     self.services.sendCloseConection()
        #     self.services = None

        #     self.txt_IP_input.config(state = 'normal')
        #     self.btn_connect.config(text = 'Connect')

    def callback(self, event):
        self.connect()

    def signUp(self):
        pass

    def signIn(self):
        window_user = Toplevel(self.master)
        userGUI(window_user, self.services)
        center(window_user)
        window_user.mainloop()

    def exit(self):
        if self.services != None:
            if not askokcancel("Exit", "Client is connecting.\nDo you want to disconnect?"):
                return
            
            # self.services.sendCloseConection()
            
        self.master.destroy()

class userGUI:
    def __init__(self, master, services):
        windowsGlo.append(master)
        self.master = master
        self.services = services
        self.master.title("User")
        # self.master.resizable(0, 0)
        self.master.focus()
        self.master.grab_set()
        self.master['padx'] = 10
        self.master['pady'] = 10

        self.btn_detail = Button(self.master, text = "Detail", command = partial(self.detail, self.master))
        self.btn_detail.grid(column = 0, row = 0, sticky = tk.W, padx = 0, pady = 0, ipadx = 20, ipady = 10)

        self.lbl_title = Label(self.master, text = 'Match List', font=("Helvetica", 16))
        self.lbl_title.grid(row = 0, column = 1, sticky = NS)

        self.btn_logout = Button(self.master, text = "Log out")
        self.btn_logout.grid(column = 2, row = 0, sticky = tk.E, padx = 0, pady = 0, ipadx = 20, ipady = 10)

        # columns
        columns = ('#1', '#2', '#3', '#4', '#5')
        self.tree = ttk.Treeview(self.master, columns = columns, show = 'headings', height = 20)

        #config column width
        self.tree.column("#1", anchor = 'center', minwidth = 50, width = 50)
        self.tree.column("#2", anchor = 'center', minwidth = 50, width = 100)
        self.tree.column("#3", anchor = 'center', minwidth = 50, width = 100)
        self.tree.column("#4", anchor = 'center', minwidth = 50, width = 50)
        self.tree.column("#5", anchor = 'center', minwidth = 50, width = 100)

        # define headings
        self.tree.heading('#1', text='ID')
        self.tree.heading('#2', text='Time')
        self.tree.heading('#3', text='Team 1')
        self.tree.heading('#4', text='Score')
        self.tree.heading('#5', text='Team 2')

        self.tree.grid(row = 1, column = 0, padx = 0, pady = 5, columnspan = 3, sticky='nsew')

        # add a scrollbar
        self.scrollbar = ttk.Scrollbar(self.master, orient = tk.VERTICAL, command = self.tree.yview)
        self.tree.configure(yscroll = self.scrollbar.set)
        self.scrollbar.grid(row = 1, column = 3, padx = 0, pady = 5, sticky = 'ns')

        # add data
        contacts = []
        contacts.append(('1', '22:10', 'Verona', '1 - 1', 'Bologna'))

        for contact in contacts:
            self.tree.insert('', tk.END, values=contact)
        
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.master.destroy()
        windowsGlo.remove(self.master)

    def detail(self, parent):
        match = self.tree.item(self.tree.focus())['values']
        if match == '':
            return

        window_detail = Toplevel(self.master)
        detailGUI(window_detail, parent, self.services, match)
        center(window_detail)
        window_detail.mainloop()

class detailGUI:
    def __init__(self, master, parent, services, match):
        windowsGlo.append(master)
        self.services = services
        self.master = master
        self.master.title("Match details")
        # self.master.resizable(0, 0)
        self.master.focus()
        self.master.grab_set()
        self.master['padx'] = 10
        self.master['pady'] = 10

        self.parent = parent

        self.lbl_ID = Label(self.master, text = match[0], font=("Helvetica", 14))
        self.lbl_ID.grid(row = 0, column = 0)

        self.lbl_time = Label(self.master, text = match[1], font=("Helvetica", 14))
        self.lbl_time.grid(row = 0, column = 1)

        self.lbl_team1 = Label(self.master, text = match[2], font=("Helvetica", 14))
        self.lbl_team1.grid(row = 0, column = 2)

        self.lbl_score = Label(self.master, text = match[3], font=("Helvetica", 14))
        self.lbl_score.grid(row = 0, column = 3)

        self.lbl_team2 = Label(self.master, text = match[4], font=("Helvetica", 14))
        self.lbl_team2.grid(row = 0, column = 4)

        # columns
        columns = ('#1', '#2', '#3', '#4', '#5', '#6')
        self.tree = ttk.Treeview(self.master, columns = columns, show = 'headings', height = 20)

        #config column width
        self.tree.column("#1", anchor = 'center', minwidth = 50, width = 50)
        self.tree.column("#2", anchor = 'center', minwidth = 50, width = 100)
        self.tree.column("#3", anchor = 'center', minwidth = 50, width = 100)
        self.tree.column("#4", anchor = 'center', minwidth = 50, width = 50)
        self.tree.column("#5", anchor = 'center', minwidth = 50, width = 100)
        self.tree.column("#6", anchor = 'center', minwidth = 50, width = 100)

        # define headings
        self.tree.heading('#1', text='Time')
        self.tree.heading('#2', text='Team 1 player')
        self.tree.heading('#3', text='Event')
        self.tree.heading('#4', text='Score')
        self.tree.heading('#5', text='Event')
        self.tree.heading('#6', text='Team 2 player')

        self.tree.grid(row = 1, column = 0, padx = 0, pady = 5, columnspan = 5, sticky='nsew')

        # add a scrollbar
        self.scrollbar = ttk.Scrollbar(self.master, orient = tk.VERTICAL, command = self.tree.yview)
        self.tree.configure(yscroll = self.scrollbar.set)
        self.scrollbar.grid(row = 1, column = 5, padx = 0, pady = 5, sticky = 'ns')

        # add data
        contacts = []
        contacts.append(("10'", 'A', 'Score', '1 - 0', '', ''))
        contacts.append(("20'", '', '', '1 - 1', 'Score', 'B'))

        for contact in contacts:
            self.tree.insert('', tk.END, values=contact)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.master.destroy()
        self.parent.focus()
        self.parent.grab_set()
        windowsGlo.remove(self.master)

window_client = Tk()
ClientGUI(window_client)
center(window_client)
window_client.mainloop()