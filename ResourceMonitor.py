import tkinter as tk
from tkinter import ttk
import psutil
from win10toast import ToastNotifier
import time

class SystemMonitor(tk.Tk):
    def __init__(self):
        self.cpu_cooldown = 0
        self.memory_cooldown = 0

        super().__init__()
        
        # 无边框,置顶
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True) 
        
        # 黑色背景
        self.config(bg='black')
        
        # 创建界面元素
        self.cpu_var = tk.StringVar()
        self.cpu_label = ttk.Label(self, textvariable=self.cpu_var, foreground='white', background='black')
        self.cpu_label.pack()
        
        self.memory_var = tk.StringVar()
        self.memory_label = ttk.Label(self, textvariable=self.memory_var, foreground='white', background='black')
        self.memory_label.pack()
        
        # 刷新数据
        self.refresh()
        
        # 绑定按键
        self.bind("<Escape>", self.close)
        
    def refresh(self):
        # 获取并显示占用
        cpu_percent = psutil.cpu_percent()
        self.cpu_var.set(f'CPU Usage: {cpu_percent}%')
        
        memory_percent = psutil.virtual_memory().percent
        self.memory_var.set(f'Memory Usage: {memory_percent}%')

        # 报警
        if cpu_percent > 90 and time.time() - self.cpu_cooldown > 60:
            toast.show_toast("CPU Warning", f'CPU Usage: {cpu_percent}%', duration=5)
            self.cpu_cooldown = time.time()

        if memory_percent > 90 and time.time() - self.memory_cooldown > 60:
            toast.show_toast("Memory Warning", f'Memory Usage: {memory_percent}%', duration=5)
            self.memory_cooldown = time.time()

        # 每秒刷新
        self.after(1000, self.refresh)

    def close(self, event):
        exit()
        # 退出
        
if __name__ == "__main__":
    toast = ToastNotifier()
    monitor = SystemMonitor()
    monitor.mainloop()