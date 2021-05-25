from tkinter import *
import tkinter as tk
from tkinter.messagebox import askokcancel, showerror
from tkinter import scrolledtext

class Server_GUI:
    def __init__(self, master):
        self.services = None
        self.master = master
        self.master.title("Server")
        self.master['padx'] = 10
        self.master['pady'] = 10

        self.btn_start = Button(self.master, text = "Start Server", width = 15, height = 4, command = self.start)
        self.btn_start.grid(row = 0, column = 0)

        self.lbl_log = Label(self.master, text = "Activity log")
        self.lbl_log.grid(row = 1, column = 0, sticky = W)

        self.result_area = scrolledtext.ScrolledText(self.master, wrap = tk.WORD, width = 46, height = 20, state = tk.DISABLED)
        self.result_area.grid(row = 2, column = 0)

        self.btn_clear = Button(self.master, text = "Clear log", command = self.clear)
        self.btn_clear.grid(row = 4, column = 0, ipadx = 20, ipady = 5)

        col_count, row_count = self.master.grid_size()
        for col in range(col_count):
            self.master.grid_columnconfigure(col, minsize = 0)
        
        for row in range(row_count):
            self.master.grid_rowconfigure(row, minsize = 10)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start(self):
        pass

    def writeLog(self, data):
        self.result_area.config(state='normal')
        self.result_area.insert(INSERT, data + '\n')
        self.result_area.config(state='disabled')
        self.result_area.see('end')

    def clear(self):
        self.result_area.config(state = 'normal')
        self.result_area.delete(1.0, END)
        self.result_area.config(state = 'disabled')

    def on_closing(self):
        self.master.destroy()


window_server = Tk()
Server_GUI(window_server)
window_server.mainloop()
