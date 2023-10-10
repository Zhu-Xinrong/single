import requests as r
import os

def err(cos = '', code1 = 0, code2 = ''):
    if cos == 'c':
        print('程序出现错误。该错误来自客户端：')
    elif cos == 's':
        print('程序出现错误。该错误来自服务器：')
    print('代码：',code1,'，描述：',code2)
    if code1 != 2:
        main()

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
    print('结果：\nAID：\t',aid,'\nBVID：\t',bvid,'\n封面：\t',pic,'\n标题：\t',title,'\n播放量：',view,'\n点赞量：',like,'\n收藏量：',favorite,'\n投币量：',coin,'\n弹幕量：',danmaku,'\n回复量：',reply,'\n转发量：',share,'\n简介：\t',desc,'\nUP主：\t',owner)
    tmp = input('你想要打开这个视频吗？（Y/N）')
    if tmp == 'Y' or tmp == 'y':
        if os.system('start https://www.bilibili.com/video/av{} > nul'.format(aid)) != 0:
            err('c',2,'ERR_CAN_NOT_OPEN_WEBSITE\n无法打开网站。请手动访问：https://www.bilibili.com/video/av{}'.format(aid))
        else:
            print('已打开网站。')
    main()

def showUser(mid,name,sex,face,sign,birthday,school):
    print('结果：\nUUID：\t',mid,'\n用户名：',name,'\n性别：\t',sex,'\n头像：\t',face,'\n简介：\t',sign,'\n生日：\t',birthday,'\n学校：\t',school)
    tmp = input('你想要打开这个人的主页吗？（Y/N）')
    if tmp == 'Y' or tmp == 'y':
        if os.system('start https://space.bilibili.com/{} > nul'.format(mid)) != 0:
            err('c',2,'ERR_CAN_NOT_OPEN_WEBSITE\n无法打开网站。请手动访问：https://space.bilibili.com/{}'.format(mid))
        else:
            print('已打开网站。')
    main()

def main():
    if os.system('ping bilibili.com -n 1 > nul') != 0:
        err('c',2,'无法连接至哔哩哔哩服务器')
    else:
        IDType = input('输入ID类型：')
        if IDType == 'e':
            exit()
        ID = input('输入ID：')
        try:
            if IDType == 'av':
                getAVideo(ID)
            elif IDType == 'bv':
                getBVideo(ID)
            elif IDType == 'uuid':
                getUser(ID)
            else:
                err('c',0,'不合法的ID类型')
        except:
            err('c',3,'未知错误')

main()