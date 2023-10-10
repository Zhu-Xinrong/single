import tkinter as tk
from tkinter import ttk
import requests as r
import tkinter.messagebox as mb
import os

def err(cos = '', code1 = 0, code2 = ''):
    error = '程序出现错误。该错误来自'
    if cos == 'c':
        error += '客户端：'
    elif cos == 's':
        error += '服务器：'
    error += ('\n代码：'+str(code1)+'，描述：'+code2)
    mb.showerror('错误', error)

def getAVideo(ID = ''):
    tmp = r.get(f'https://api.bilibili.com/x/web-interface/view?aid={ID[2:]}').json()
    if tmp['code'] != 0:
        err('s',tmp['code'],tmp['message'])
    else:
        tmp = tmp['data']
        showVideo(tmp['aid'],tmp['bvid'],tmp['pic'],tmp['title'],tmp['stat']['view'],tmp['stat']['like'],tmp['stat']['favorite'],tmp['stat']['coin'],tmp['stat']['danmaku'],tmp['stat']['reply'],tmp['stat']['share'],tmp['desc'],tmp['owner']['name'])

def getBVideo(ID = ''):
    tmp = r.get(f'https://api.bilibili.com/x/web-interface/view?bvid={ID}').json()
    if tmp['code'] != 0:
        err('s',tmp['code'],tmp['message'])
    else:
        tmp = tmp['data']
        showVideo(tmp['aid'],tmp['bvid'],tmp['pic'],tmp['title'],tmp['stat']['view'],tmp['stat']['like'],tmp['stat']['favorite'],tmp['stat']['coin'],tmp['stat']['danmaku'],tmp['stat']['reply'],tmp['stat']['share'],tmp['desc'],tmp['owner']['name'])

def getUser(ID = ''):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63'}
    tmp = r.get(f'https://api.bilibili.com/x/space/wbi/acc/info?mid={ID}&token=&platform=web&web_location=1550101&w_rid=bb7b26185b25e444fdaef35ce535f2d1&wts=1696945346',headers=headers).json()
    if tmp['code'] != 0:
        err('s',tmp['code'],tmp['message'])
    else:
        tmp = tmp['data']
        showUser(tmp['mid'],tmp['name'],tmp['sex'],tmp['face'],tmp['sign'],tmp['birthday'],tmp['school']['name'])

def showVideo(aid,bvid,pic,title,view,like,favorite,coin,danmaku,reply,share,desc,owner):
    if mb.askyesno('结果：', 'AID：\t'+str(aid)+'\nBVID：\t'+str(bvid)+'\n封面：\t'+str(pic)+'\n标题：\t'+str(title)+'\n播放量：'+str(view)+'\n点赞量：'+str(like)+'\n收藏量：'+str(favorite)+'\n投币量：'+str(coin)+'\n弹幕量：'+str(danmaku)+'\n回复量：'+str(reply)+'\n转发量：'+str(share)+'\n简介：\t'+str(desc)+'\nUP主：\t'+str(owner)+ '\n打开这个视频吗？'):
        if os.system('start https://www.bilibili.com/video/av{} > nul'.format(aid)) != 0:
            err('c',2,'ERR_CAN_NOT_OPEN_WEBSITE\n无法打开网站。请手动访问：https://www.bilibili.com/video/av{}'.format(aid))

def showUser(mid,name,sex,face,sign,birthday,school):
    if mb.askyesno('结果：', 'UUID：\t'+str(mid)+'\n用户名：'+str(name)+'\n性别：\t'+str(sex)+'\n头像：\t'+str(face)+'\n简介：\t'+str(sign)+'\n生日：\t'+str(birthday)+'\n学校：\t'+str(school)+'\n打开个人主页吗？'):
        if os.system('start https://space.bilibili.com/{} > nul'.format(mid)) != 0:
            err('c',2,'ERR_CAN_NOT_OPEN_WEBSITE\n无法打开网站。请手动访问：https://space.bilibili.com/{}'.format(mid))

def on_get_info():
    id_type = id_type_var.get()
    id_value = id_entry.get()
    if id_type == 'av':
        getAVideo(id_value)
    elif id_type == 'bv':
        getBVideo(id_value)
    elif id_type == 'uuid':
        getUser(id_value)
    else:
        err('c', 0, '不合法的ID类型')

root = tk.Tk()
root.title("信息获取器")

id_type_var = tk.StringVar()
id_type_var.set('av')

id_type_label = ttk.Label(root, text="ID 类型:")
id_type_label.grid(column=0, row=0)

id_type_av = ttk.Radiobutton(root, text="AV", variable=id_type_var, value="av")
id_type_av.grid(column=1, row=0)

id_type_bv = ttk.Radiobutton(root, text="BV", variable=id_type_var, value="bv")
id_type_bv.grid(column=2, row=0)

id_type_uuid = ttk.Radiobutton(root, text="UUID", variable=id_type_var, value="uuid")
id_type_uuid.grid(column=3, row=0)

id_label = ttk.Label(root, text="ID:")
id_label.grid(column=0, row=1)

id_entry = ttk.Entry(root)
id_entry.grid(column=1, row=1, columnspan=3)

get_info_button = ttk.Button(root, text="获取信息", command=on_get_info)
get_info_button.grid(column=2, row=2)

root.mainloop()