from tkinter import *
import tkinter as tk
from tkinter.messagebox import askokcancel, showerror
from tkinter import scrolledtext
import server
from queue import SimpleQueue

class Server_GUI:
    def __init__(self, master):
        self.services = None
        self.master = master
        self.msg = SimpleQueue()
        self.master.title("Server")
        self.master['padx'] = 15
        self.master['pady'] = 15

        self.btn_start = Button(self.master, text = "Start Server", font=(None, 12), width = 25, height = 3, command = self.start)
        self.btn_start.grid(row = 0, column = 0, rowspan = 2, columnspan = 2, ipady = 5, sticky = W)

        self.btn_clear = Button(self.master, text = "Clear log", width = 13, height = 1, command = self.clear)
        self.btn_clear.grid(row = 0, column = 2, sticky = NE, ipady = 3, padx = 15)

        self.btn_exit = Button(self.master, text = "Exit", width = 13, height = 1, command = self.on_closing)
        self.btn_exit.grid(row = 1, column = 2, sticky = SE, ipady = 3, padx = 15)

        self.lbl_currClientsNum = Label(self.master)
        self.lbl_currClientsNum.grid(row = 1, column = 3, sticky = SW, pady = 6)
        
        self.lbl_max = Label(self.master, text = "Maximum number of clients:")
        self.lbl_max.grid(row = 0, column = 3, sticky = SW)

        self.maxClients = tk.IntVar(value = 5)
        self.spinmaxClients = tk.Spinbox(self.master, width = 3,font=(None, 12), from_=0, to=30, textvariable=self.maxClients, wrap=True)
        self.spinmaxClients.place(x = 535, y = 15)

        self.lbl_log = Label(self.master, text = "Activity log")
        self.lbl_log.grid(row = 2, column = 0, sticky = W)

        self.result_area = scrolledtext.ScrolledText(self.master, wrap = tk.WORD, width = 70, height = 30, state = tk.DISABLED)
        self.result_area.grid(row = 3, column = 0, columnspan = 5)


        col_count, row_count = self.master.grid_size()
        for col in range(col_count):
            self.master.grid_columnconfigure(col, minsize = 30)
        
        for row in range(row_count):
            self.master.grid_rowconfigure(row, minsize = 20)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.monitor_queue()

    def monitor_queue(self):
        while not self.msg.empty():
            data = self.msg.get()
            self.result_area.config(state='normal')
            self.result_area.insert(INSERT, data + '\n')
            self.result_area.config(state='disabled')
            self.result_area.see('end')

            if self.services is None:
                self.lbl_currClientsNum.config(text = '')
            else:
                self.lbl_currClientsNum.config(text = 'Number of connected clients: ' + str(self.services.clientCount[0]))

        self.master.after(100, self.monitor_queue)

    def start(self):
        if self.services is None:
            try:
                self.services = server.Server(self.msg, int(self.spinmaxClients.get()))
                self.services.start()
            except:
                self.services = None
                showerror('Error', 'Unable to start server', parent = self.master)
            else:
                self.btn_start.config(text = "Stop Server")
                self.spinmaxClients.config(state = 'disabled')

        else:
            if self.services.clientCount[0] > 0 and not askokcancel("Stop", f"{self.services.clientCount[0]} client(s) is connecting.\nDo you really want to stop server?"):
                return

            self.services.stop()
            self.services = None
            
            self.btn_start.config(text = "Start Server")
            self.spinmaxClients.config(state = 'normal')

    def clear(self):
        self.result_area.config(state = 'normal')
        self.result_area.delete(1.0, END)
        self.result_area.config(state = 'disabled')

    def on_closing(self):
        if self.services is not None:
            if askokcancel("Quit", "Server is running.\nDo you want to quit?"):
                if self.services.clientCount[0] > 0 and not askokcancel("Stop", f"{self.services.clientCount[0]} client(s) is connecting.\nDo you really want to exit?"):
                    return
                self.services.stop()
            else:
                return
                
        self.master.destroy()


window_server = Tk()
Server_GUI(window_server)
window_server.mainloop()
