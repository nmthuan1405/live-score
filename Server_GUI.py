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

        self.btn_start = Button(self.master, text = "Start Server", font=(None, 12), width = 16, height = 3, command = self.start)
        self.btn_start.grid(row = 0, column = 1, rowspan = 2, ipady = 5)

        self.btn_clear = Button(self.master, text = "Clear log", width = 10, height = 1, command = self.clear)
        self.btn_clear.grid(row = 0, column = 2, sticky = NW, ipady = 3)

        self.btn_exit = Button(self.master, text = "Exit", width = 10, height = 1, command = self.exit)
        self.btn_exit.grid(row = 1, column = 2, sticky = SW, ipady = 3)

        self.lbl_log = Label(self.master, text = "Activity log")
        self.lbl_log.grid(row = 2, column = 0, sticky = W)

        self.result_area = scrolledtext.ScrolledText(self.master, wrap = tk.WORD, width = 60, height = 30, state = tk.DISABLED)
        self.result_area.grid(row = 3, column = 0, columnspan = 4)


        col_count, row_count = self.master.grid_size()
        for col in range(col_count):
            self.master.grid_columnconfigure(col, minsize = 50)
        
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

        self.master.after(100, self.monitor_queue)

    def start(self):
        if self.services is None:
            try:
                self.services = server.Server(self.msg)
                self.services.start()
            except:
                self.services = None
                showerror('Error', 'Unable to start server', parent = self.master)
            else:
                self.btn_start.config(text = "Stop Server")

        else:
            count = self.services.clientCount()
            if count > 0 and not askokcancel("Stop", f"{count} client(s) is connecting.\nDo you really want to stop server?"):
                return

            self.services.stop()
            self.services = None
            
            self.btn_start.config(text = "Start Server")

    def clear(self):
        self.result_area.config(state = 'normal')
        self.result_area.delete(1.0, END)
        self.result_area.config(state = 'disabled')

    def exit(self):
        self.on_closing()

    def on_closing(self):
        if self.services is not None:
            if askokcancel("Quit", "Server is running.\nDo you want to quit?"):
                count = self.services.clientCount()
                
                if count > 0 and not askokcancel("Stop", f"{count} client(s) is connecting.\nDo you really want to exit?"):
                    return

                self.services.stop()
            else:
                return

        self.master.destroy()


window_server = Tk()
Server_GUI(window_server)
window_server.mainloop()
