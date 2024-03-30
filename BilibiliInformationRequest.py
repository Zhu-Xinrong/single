'''
    Copyright (c) Kendall 2023 - 2024. All rights reserved.
    LastUpdate  03/30/2024 Sat.
'''
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
from PIL import Image, ImageTk
import os, json, requests

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'}

# 定义错误处理函数
def display_error(error_source, error_code1, error_code2=None):
    error_message = '出现错误。该错误来自'
    if error_source == 'c':
        error_message += '客户端'
    elif error_source == 's':
        error_message += '服务器'
    error_message += ('\n代码{}：{}\n'.format(error_code1, error_code2 if error_code2 else ''))
    mb.showerror('错误', error_message)

# 定义获取信息函数
def getInfo(ID = ''):
    try:
        links = [f'https://api.bilibili.com/x/web-interface/view?aid={ID[2:]}', f'https://api.bilibili.com/x/web-interface/view?bvid={ID}', f'https://api.bilibili.com/x/space/acc/info?mid={ID}']
        if ID[:2] == 'av':
            IDType = 0
        elif ID[:2] == 'BV':
            IDType = 1
        data = requests.get(links[IDType], headers = headers).json()
        if data['code'] != 0:
            return 'error', data['code'], data['message']
        else:
            data = data['data']
            return 'video', data['aid'], data['bvid'], data['pic'], data['title'], data['stat']['view'], data['stat']['like'], data['stat']['favorite'], data['stat']['coin'], data['stat']['danmaku'], data['stat']['reply'], data['stat']['share'], data['desc'], data['owner']['name']
    except Exception as e:
        return 'error', 0, f'无法连接到服务器：{e}'

# 定义显示视频函数
def showVideo(result = ()):
    video_window = tk.Toplevel()
    video_window.title("视频信息")

    open('cover.jpg', 'wb').write(requests.get(result[2]).content)

    result = list(result)
    result.pop(2)
    # 创建标签和布局
    labels = []
    for i, text in enumerate(["AID", "BVID", "标题", "播放量", "点赞量", "收藏量", "投币量", "弹幕量", "评论量", "分享量", "简介", "UP主"]):
        label = tk.Label(video_window, text=f"{text}: {result[i]}", anchor="w", padx=10, pady=5)
        label.grid(row=i, column=0, sticky="w")
        labels.append(label)

    # 显示图片
    try:
        image = Image.open('cover.jpg')
        image = image.resize((480, 300), resample = Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        image_label = tk.Label(video_window, image=photo)
        image_label.image = photo  # 防止图片垃圾回收
        image_label.grid(row=0, rowspan=len(labels), column=1, padx=10)
    except Exception as e:
        display_error('c', 1, f"无法显示图片：{e}")

    # 打开链接按钮
    open_link = tk.Button(video_window, text="打开", command=lambda: openLink(result[0]))
    open_link.grid(row=len(labels), columnspan=2, pady=10)

    video_window.mainloop()

def openLink(aid = 0):
    os.system('start https://www.bilibili.com/video/av{} > nul'.format(aid))
    
def process(id_value = '', batch = False):
    temp = getInfo(id_value)
    if temp[0] != 'error':
        if batch != True:
            showVideo(temp[1:])
        else:
            return temp[1:]
    else:
        display_error('s', temp[1], temp[2])
        return None

# 定义获取信息函数
def on_get_info():
    id_value = id_entry.get()
    if id_value != 'batch':
       process(id_value)
    else:
        result = {}
        if mb.askokcancel('确认？', '将读取运行目录下的"videoList.json"文件，请参照"README.md"中有关批量查询的说明填写。继续？'):
            with open('videoList.json', 'r') as f:
                data = json.load(f)
            success = True
            for video in data['videoList']:
                temp = process(video, True)
                if temp == None:
                    mb.showerror('错误', f'在获取{video}时出现错误。已停止整个操作。')
                    success = False
                    break
                else:
                    result[video] = temp
            if success == True:
                datas = {
                    'AID': [result[video][0] for video in result],
                    'BVID': [result[video][1] for video in result],
                    '标题': [result[video][3] for video in result],
                    '播放量': [result[video][4] for video in result],
                    '点赞量': [result[video][5] for video in result],
                    '收藏量': [result[video][6] for video in result],
                    '投币量': [result[video][7] for video in result],
                    '弹幕量': [result[video][8] for video in result],
                    '评论量': [result[video][9] for video in result],
                    '分享量': [result[video][10] for video in result],
                    'UP主': [result[video][12] for video in result]
                }
                file = '<!DOCTYPE html>\n<head>\n<title>' + str(len(data['videoList'])) + '个视频的查询结果</title>\n</head>\n<body>\n<table border="' + str(data['border']) + '">\n<thead><tr>\n'
                for key in datas:
                    file += f'<th>{key}</th>\n'
                file += '</tr></thead>\n<tbody>\n'
                for i in range(len(data['videoList'])):
                    file += '<tr>\n'
                    for key in datas:
                        file += f'<td>{datas[key][i]}</td>\n'
                    file += '</tr>\n'
                file += '</tbody>\n</table>\n</body>\n</html>'
                with open('result.html', 'w') as f:
                    f.write(file)
                mb.showinfo('成功', '生成的结果已保存在程序所在目录下的 result.html 中。')
        else:
            mb.showinfo('已取消', '已取消')

if __name__ == '__main__':
    root = tk.Tk()
    root.title("BIR")

    id_label = ttk.Label(root, text="ID ")
    id_label.grid(column=0, row=1)

    id_entry = ttk.Entry(root)
    id_entry.grid(column=1, row=1, columnspan=3)

    get_info_button = ttk.Button(root, text="获取信息", command=on_get_info)
    get_info_button.grid(column=2, row=2)

    root.mainloop()