'''
    Copyright (c) Kendall 2023 - 2024. All rights reserved.
    LastUpdate  03/30/2024 Sat.
'''
import requests, ctypes, os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

def get():
    data = requests.get('https://cn.bing.com/HPImageArchive.aspx', params = {'format': 'js', 'idx': 0, 'n': 1, 'mkt': 'zh-CN'}).json()['images'][0]
    title = data['title']
    enddate = data['enddate']
    url = 'https://cn.bing.com' + data['url']
    copyright = data['copyright']
    return title, enddate, copyright, url

def show(result = ()):
    root = tk.Tk()
    root.title(result[0] + ' - ' + result[1] + ' - 必应每日图片')

    open(f'.\\BingImage\\{result[1]}.jpg', 'wb').write(requests.get(result[3]).content)

    labels = []
    for i, text in enumerate(['标题', '日期', '版权']):
        label = tk.Label(root, text = f'{text}：{result[i]}', anchor = 'w', padx = 10, pady = 5)
        label.grid(row = i + 1, column = 0, sticky = 'w')
        labels.append(label)
    
    image = Image.open(f'.\\BingImage\\{result[1]}.jpg')
    image = image.resize((720, 405), resample = Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image)
    image_label = tk.Label(root, image = photo)
    image_label.image = photo
    image_label.grid(row = 0, column = 0, sticky = 'nsew')

    set_wallpaper = tk.Button(root, text = '设置为壁纸', command = lambda: setWallpaper(result[1]))
    set_wallpaper.grid(row = 4, column = 0)

    root.mainloop()

def setWallpaper(name = ''):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.split(os.path.realpath(__file__))[0] + '\\BingImage\\' + name + '.jpg', 3)

try:
    show(get())
except Exception as e:
    messagebox.showerror('发生了错误', str(e))