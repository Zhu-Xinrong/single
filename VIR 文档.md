# 视频信息获取器 设计思路及给用户和开发者的文档

## 介绍
VIR，全称 Video Information Request。这是一个使用 Python 编写完成的应用，支持对以下平台的视频信息的获取：

| 平台 | 官网 | 支持的类型 | 在程序内部的定义 |
| ------- | ------- |  ------- |  ------- | 
| 哔哩哔哩 | [https://www.bilibili.com/](https://www.bilibili.com/) | AV号、BV号、专栏号 | blbl |

更多的还在适配当中。<br>这个应用的前身是 BilibiliInformationRequest。但其已经有一年的历史，加上注释写不勤，导致可读性变差。目前该应用已不再维护，由它的后辈接替今后的新功能更新。由于搬迁需要一定时间，目前已有 0/7 个功能完成了搬迁。在每个函数的介绍中可看到目前该函数的更新状态(Coming S∞n/Completed/Fixing bugs)。在搬迁完成之前大概率不会增加新功能。

## 程序大体思路及给开发者的文档

该文件本身可以作为一个模块导入。
1. 确保你的程序与 VIR.py 在同一目录下；
2. 使用```import VIR```导入；
3. 在代码中使用```data = VIR.process(platform = "blbl", id = "av706")```等类似的代码使用。

### 函数 process()
#### 状态
Completed
#### 作用
获取信息
#### 传入的参数
```process(platform = "", id = "")```
#### 对传入的参数的解释
platform：字符串，表示该 ID 来自于哪个平台。具体见上文：介绍 - 在程序内部的定义。<br>
id：字符串，具体的 ID 值。
#### 大致原理
函数中会先对 platform 中的平台进行判断。若支持该平台，则返回结果；若该平台不支持，则会返回 ```None```。<br>随后使用网站的 API 获取该 ID 的信息，解析并返回。若出现错误，如```code```的值不为0，则返回具体的错误消息，如```msg```中的内容。正常情况下返回值是一个字典，包含目前已适配的返回内容。具体见下文：程序大体思路 - 函数 process() - 返回内容。**函数本身不会处理如网络错误等错误，需要开发者自行添加 try except。**
#### 返回内容
##### 哔哩哔哩
###### AV 号和 BV 号
```
{
	"type": "video", 
	"aid": 706, 
	"bvid": "BV1xx411c79H", 
	"pic": "http://i1.hdslb.com/bfs/archive/753453a776fca838165a52c7511e8557857b61ea.jpg", 
	"title": "【東方】Bad Apple!! ＰＶ【影絵】", 
	"videos": 1, 
	"tname": "短片·手书", 
	"pubdate": 1256995125, 
	"view": 10875621, 
	"like": 458409, 
	"favorite": 488940, 
	"coin": 188408, 
	"danmaku":  81562, 
	"reply": 535546, 
	"share": 91670, 
	"desc": "sm8628149 2011/9/25追记：大家如果看到空耳字幕请果断举报，净化弹幕环境，你我有责，感谢。", 
	"name": "折射", 
	"mid": 37
}
```
###### 专栏号
```
{
	"type": "article", 
	"title": "【明日方舟同人/桃】当博士与德克萨斯被困在了不XX就无法出去的房间", 
	"view": 2312, 
	"favorite": 28, 
	"like": 94, 
	"reply": 3, 
	"share": 0, 
	"coin": 5, 
	"author_name": "教主别冲了-AFan", 
	"mid": 1420619473, 
	"origin_image_urls": ["https://i0.hdslb.com/bfs/new_dyn/b3f22b6eb7d0501f8f2a6694adf2bb5b1420619473.jpg"], 
	"video_url": "", 
	"id": "cv33714863"
}
```
###### 出现错误
```
{
	'type': 'error',
	'message': '稿件不可见'
}
```

### 函数 showVideo()
#### 状态
Completed
#### 作用
展示视频信息
#### 传入的参数
```showVideo(platform = "", data = {})```
#### 对传入的参数的解释
platform：同上<br>
data：列表，表示获取到的信息
#### 大致的原理
函数会使用```tkinker```模块创建一个窗口。下载封面并保存到程序所在目录下的 cover.jpg 中。<br>在左侧显示获取的信息，右侧是封面（尺寸为 480x300）。下方有两个按钮，一个用于打开视频原链接，一个用于打开创作者的主页。

### 函数 showArticle()
#### 状态
Completed
#### 作用
展示文章信息
#### 传入的参数
同上
#### 大致的原理
同上

### 函数 display_error()
#### 状态
Completed
#### 作用
在发生错误时弹出错误窗口
#### 传入的参数
```display_error(message = "")```
#### 对传入的参数的结束
message：具体的错误消息
#### 大致的原理
函数会使用```tkinker.messagebox.showerror()```弹出错误窗口。

### 函数 export()
#### 状态
Coming S∞n
#### 作用
将获取的信息导出至指定的 .html 文件
#### 传入的参数
```export(type_ = "", name = "", data = {}, pic = '')```
#### 对传入的参数的解释
type_：字符串，表示数据的类型，即 video 或 article<br>
data：同上<br>
name：字符串，表示导出的文件名<br>
pic：字符串，表示封面的 URL
#### 大致的原理
函数会解析传入的数据，并将数据导出至 name 中