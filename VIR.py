'''
    Copyright (c) Kendall 2023 - 2024. All rights reserved.
    Last Updated: 2024/04/13
'''
# 模块导入
import requests, time, os
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import IntVar, ttk
import tkinter.messagebox as mb
# 基本参数
call = True
version = '0.0.1'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0'}

def process(platform = '', id = ''):
    platforms = ['blbl']
    if platform in platforms:   # 若平台已适配
        if platform == 'blbl':  #若该平台为 B站
            urls = [f'https://api.bilibili.com/x/web-interface/view?aid={id[2:]}', f'https://api.bilibili.com/x/web-interface/view?bvid={id}', f'https://api.bilibili.com/x/article/viewinfo?id={id[2:]}']
            # 判断 id 类型
            if id[:2] == 'av':
                idType = 0
            elif id[:2] == 'BV':
                idType = 1
            elif id[:2] == 'cv':
                idType = 2
            # 获取数据
            else:
                return None
            data = requests.get(urls[idType], headers = headers).json()
            # 判断是否出现错误
            if data['code'] == 0:
                data = data['data']
                if idType < 2:  # 如果是视频，返回：
                    return {
                        'type': 'video', 
                        'aid': data['aid'], 
                        'bvid': data['bvid'], 
                        'pic': data['pic'], 
                        'title': data['title'], 
                        'videos': data['videos'], 
                        'tname': data['tname'],
                        'pubdate': data['pubdate'], 
                        'view': data['stat']['view'], 
                        'like': data['stat']['like'], 
                        'favorite': data['stat']['favorite'], 
                        'coin': data['stat']['coin'],
                        'danmaku': data['stat']['danmaku'], 
                        'reply': data['stat']['reply'], 
                        'share': data['stat']['share'],
                        'desc': data['desc'], 
                        'name': data['owner']['name'], 
                        'mid': data['owner']['mid']
                    }
                else:   # 如果是专栏，返回：
                    return {
                        'type': 'article', 'title': data['title'], 'view': data['stats']['view'], 'favorite': data['stats']['favorite'], 'like': data['stats']['like'], 'reply': data['stats']['reply'], 'share': data['stats']['share'], 'coin': data['stats']['coin'], 'author_name': data['author_name'], 'mid': data['mid'], 'origin_image_urls': data['origin_image_urls'], 'video_url': data['video_url'], 'id': id
                    }
            else:   # 如果发生错误，返回：
                return {
                    'type': 'error', 
                    'message': data['message']
                }
        else:
            return None
    else:
        return None

def openLink(url = ''):
    os.system(f'start {url}')

def showAllDesc(desc = '', title = ''):
    show_all_desc_window = tk.Toplevel()
    show_all_desc_window.title(f'《{title}》完整的简介')
    show_all_desc_window.resizable(False, False)

    text = tk.Text(show_all_desc_window)
    text.insert(0.0, desc)
    text.grid(row = 0, column = 0, sticky = 'nsew')

    show_all_desc_window.mainloop()

def showVideo(platform = '', data = {}):
    # 创建窗口
    video_window = tk.Toplevel()
    video_window.title('视频《' + data['title'] + '》的信息')
    video_window.resizable(False, False)

    open('cover.jpg', 'wb').write(requests.get(data['pic'], headers = headers).content) # 下载封面

    type_ = data['type']
    pic = data['pic']
    del data['pic'], data['type']
    too_long = False
    data['pubdate'] = time.strftime('%Y年%m月%d日 %H:%M:%S', time.localtime(data['pubdate']))
    if len(data['desc']) > 250:
        all_desc = data['desc']
        data['desc'] = data['desc'][:250] + '...'
        too_long = True

    # 在左侧创建标签
    labels = []
    for i, text in enumerate(['AID', 'BVID', '标题', '视频数', '分区', '发布时间', '播放量', '点赞数', '收藏数', '硬币数', '弹幕数', '评论数', '分享数', '简介', '创作者']):
        values = list(data.values())
        label = tk.Label(video_window, text = f'{text}\t{values[i]}')
        label.grid(row = i, column = 0, sticky = 'w')
        labels.append(label)

    # 在右侧显示封面
    image = Image.open('cover.jpg')
    image = image.resize((480, 300), resample = Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image)
    image_label = tk.Label(video_window, image = photo)
    image_label.grid(row = 0, column = 1, sticky = 'nsew', rowspan = len(labels))

    urls = []
    if platform == 'blbl':
        urls = ['https://www.bilibili.com/video/av' + str(data['aid']), 'https://space.bilibili.com/' + str(data['mid'])]
    # 在下方的按钮
    open_link_button_0 = tk.Button(video_window, text = '打开此视频', command = lambda: openLink(urls[0]))
    open_link_button_0.grid(row = 0, column = 2)
    open_link_button_1 = tk.Button(video_window, text = '打开创作者主页', command = lambda: openLink(urls[1]))
    open_link_button_1.grid(row = 1, column = 2)
    if too_long:
        show_all_desc_button = tk.Button(video_window, text = '显示全部简介', command = lambda: showAllDesc(all_desc, data['title']))
        show_all_desc_button.grid(row = 2, column = 2)
    export_button = tk.Button(video_window, text = '导出信息', command = lambda: export(type_, data['title'] + '.html', data, pic))
    export_button.grid(row = 2 + int(too_long), column = 2)

    video_window.mainloop()

def showArticle(data = {}):
    # 创建窗口
    article_window = tk.Toplevel()
    article_window.title('专栏《' + data['title'] + '》的信息')
    article_window.resizable(False, False)

    open('cover.jpg', 'wb').write(requests.get(str(data['origin_image_urls'])[2:-2], headers = headers).content)    # 下载封面

    # 在左侧创建标签
    type_ = data['type']
    pic = data['origin_image_urls'][0]
    del data['origin_image_urls'], data['type']
    labels = []
    for i, text in enumerate(['标题', '播放量', '收藏量', '点赞量', '评论量', '分享量', '投币量', '创作者']):
        values = list(data.values())
        label = tk.Label(article_window, text=f'{text}\t{values[i]}', anchor='w', padx=10, pady=5)
        label.grid(row = i, column = 0, sticky = 'w')
        labels.append(label)
    
    # 在中部显示封面
    image = Image.open('cover.jpg')
    if image.size[0] > image.size[1]:
        width = 480
        height = 300
    else:
        width = 300
        height = 480
    image = image.resize((width, height), resample = Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image)
    image_label = tk.Label(article_window, image=photo)
    image_label.image = photo
    image_label.grid(row=0, rowspan=len(labels), column=1, padx=10)

    # 在右侧的按钮
    open_link0 = tk.Button(article_window, text='打开此专栏', command = lambda: openLink('https://www.bilibili.com/read/' + data['id']))
    open_link0.grid(row = 0, column = 2,columnspan=2, pady=10)
    open_link1 = tk.Button(article_window, text='打开UP主主页', command = lambda: openLink('https://space.bilibili.com/' + str(data['mid'])))
    open_link1.grid(row = 1, column = 2, columnspan=2, pady=10)
    export_button = tk.Button(article_window, text='导出信息', command=lambda: export(type_, data['title'] + '.html', data, pic))
    export_button.grid(row = 2, column=2, columnspan=2, pady=10)

    article_window.mainloop()

def export(type_ = '', name = '', data = {}, pic = ''):
    content = '<!DOCTYPE html>\n<html>\n<head>\n<title>《' + data['title'] + '》的信息</title>\n</head>\n<body>\n'
    if type_ == 'video':
        for i, text in enumerate(['AID', 'BVID', '标题', '视频数', '分区', '发布时间', '播放量', '点赞数', '收藏数', '硬币数', '弹幕数', '评论数', '分享数', '简介', '创作者']):
            values = list(data.values())
            content += f'<p>{text}: {values[i]}</p>\n'
        content += '<img src="' + pic + '" alt="封面" style="width: 480px; height: 300px;">\n'
    elif type_ == 'article':
        for i, text in enumerate(['标题', '播放量', '收藏量', '点赞量', '评论量', '分享量', '投币量', '创作者']):
            values = list(data.values())
            content += f'<p>{text}: {values[i]}</p>\n'
        content += '<img src="' + pic + '" alt="封面">\n'
    content += '</body>\n</html>'
    if name.find('\\') != -1:
        name = name.replace('\\', '-')
    elif name.find('/') != -1:
        name = name.replace('/', '-')
    open(name, 'w', encoding = 'utf-8').write(content)
        
def getInfo(platform = 0, id = ''):
    if platform == 0:
        data = process('blbl', id)
        if data == None:
            display_error('未知 ID 类型')
        elif data['type'] == 'error':
            display_error(data['message'])
        elif data['type'] == 'video':
            showVideo('blbl', data)
        elif data['type'] == 'article':
            showArticle(data)
            
def display_error(message = ''):
    mb.showerror('错误', message)

if __name__ == '__main__':
    call = False
    
    # 创建窗口
    root = tk.Tk()
    root.title('VIR')
    root.resizable(False, False)

    # 创建单选框
    selected_value = IntVar()
    blbl = tk.Radiobutton(root, text = '哔哩哔哩', variable = selected_value, value = 0)
    blbl.grid(row = 0, column = 0)
    blbl.select()

    # 创建标签
    id_label = ttk.Label(root, text = 'ID: ')
    id_label.grid(row = 1, column = 0)

    # 创建输入框
    id_entry = ttk.Entry(root)
    id_entry.grid(row = 1, column = 1)

    # 创建按钮
    get_info_button = ttk.Button(root, text = '获取信息', command = lambda: getInfo(selected_value.get(), id_entry.get()))
    get_info_button.grid(row = 2, column = 0, columnspan = 2)

    root.mainloop()
else:
    print('VIR Version', version, 'by KendallZXR.')