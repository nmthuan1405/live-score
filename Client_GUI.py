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

        self.btn_connect = Button(self.master, text="Connect")
        self.btn_connect.grid(column=2, row=2, sticky = tk.E, padx = 0, pady = 0, ipadx = 10)

        self.lbl_User = Label(self.master, text = "Username")
        self.lbl_User.grid(column = 0, row = 4, sticky = tk.W, padx = 0, pady = 0)

        self.txt_User = Entry(self.master)
        self.txt_User.grid(column = 0, row = 5, columnspan = 3, sticky = EW)

        self.lbl_Password = Label(self.master, text = "Password")
        self.lbl_Password.grid(column = 0, row = 6, sticky = tk.W, padx = 0, pady = 0)

        self.txt_Password = Entry(self.master)
        self.txt_Password.grid(column = 0, row = 7, columnspan = 3, sticky = EW)

        self.btn_SignUp = Button(self.master, text="Sign Up")
        self.btn_SignUp.grid(column=0, row=9, rowspan = 2, sticky = tk.SW, padx = 0, pady = 0, ipadx = 10)

        self.btn_SignIn = Button(self.master, text="Sign In")
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
        showerror(title = 'Error', message = 'Lost connection')

    def exit(self):
        if self.services != None:
            if not askokcancel("Exit", "Client is connecting.\nDo you want to disconnect?"):
                return
            
            # self.services.sendCloseConection()
            
        self.master.destroy()


window_client = Tk()
ClientGUI(window_client)
center(window_client)
window_client.mainloop()