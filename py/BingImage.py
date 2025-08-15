'''
    Copyright (c) Kendall 2025. All rights reserved.
    Last Updated: 2025/8/1
'''
import requests, ctypes, winreg, os, sys, json, tkinter as tk, webbrowser
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from io import BytesIO
from win32com.client import Dispatch

# 初始化
Win = os.name == 'nt'
# Win = False
REG_PATH = r'Software\Kendall\BingImage'
FOLDER_PATH_KEY = 'FolderPath'
SAVE_HISTORY_KEY = 'SaveHistory'
DEFAULT_FOLDER = os.path.split(os.path.abspath(__file__))[0]

try:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH)
    folder_path = winreg.QueryValueEx(key, FOLDER_PATH_KEY)[0]
    save_history = bool(winreg.QueryValueEx(key, SAVE_HISTORY_KEY)[0])
    winreg.CloseKey(key)
except FileNotFoundError:
    folder_path = DEFAULT_FOLDER
    save_history = True

def update_registry():
    '''更新注册表设置'''
    global save_history, folder_path
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        winreg.SetValueEx(key, FOLDER_PATH_KEY, 0, winreg.REG_SZ, folder_path)
        winreg.SetValueEx(key, SAVE_HISTORY_KEY, 0, winreg.REG_DWORD, 1 if save_history else 0)
        winreg.CloseKey(key)
    except Exception as e: messagebox.showerror('注册表错误', f'更新注册表时出错: {str(e)}。')

update_registry()

class SettingsDialog(tk.Toplevel):
    '''配置对话框'''
    def __init__(self, parent):
        super().__init__(parent)
        self.title('配置设置')
        self.resizable(False, False)
        self.transient(parent)
        self.focus_set()
        self.grab_set()

        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
        
        # 创建变量
        self.folder_var = tk.StringVar(value=folder_path)
        self.save_history_var = tk.BooleanVar(value=save_history)
        
        # 创建框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 文件夹路径设置
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text='保存位置：').pack(side=tk.LEFT, padx=(0, 5))
        self.path_entry = ttk.Entry(path_frame, textvariable=self.folder_var, width=40)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(path_frame, text='浏览', command=self.browse_folder)
        browse_btn.pack(side=tk.LEFT)
        
        # 历史保存选项
        history_frame = ttk.Frame(main_frame)
        history_frame.pack(fill=tk.X, pady=5)
        
        history_cb = ttk.Checkbutton(history_frame, text='保存历史图片', variable=self.save_history_var)
        history_cb.pack(anchor=tk.W)
        
        # 说明文本
        ttk.Label(main_frame, text='禁用历史保存将覆盖同一个文件（Wallpaper.jpg），否则以日期命名。', foreground='gray').pack(anchor=tk.W, pady=(0, 10))
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text='恢复默认', command=self.restore_default).pack(side=tk.LEFT)
        ttk.Button(button_frame, text='确定', command=self.save).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text='取消', command=self.destroy).pack(side=tk.RIGHT)
    
    def browse_folder(self):
        '''打开文件夹选择对话框'''
        folder = filedialog.askdirectory(initialdir=self.folder_var.get())
        if folder: self.folder_var.set(folder)
    
    def restore_default(self):
        '''恢复默认设置'''
        self.folder_var.set(DEFAULT_FOLDER)
        self.save_history_var.set(True)
    
    def save(self):
        '''保存设置并关闭对话框'''
        global save_history, folder_path
        folder_path = self.folder_var.get()
        save_history = self.save_history_var.get()
        
        if not os.path.isdir(folder_path):
            messagebox.showerror('错误', f'{folder_path} 文件夹不存在。')
            return
        
        # 保存到父窗口
        update_registry()
        messagebox.showinfo('成功', '设置已保存。')
        self.destroy()

class BingImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title('必应每日壁纸')
        self.root.geometry('800x600')
        self.root.resizable(False, False)
        
        # 创建菜单栏
        menubar = tk.Menu(root)
        menubar.add_command(label='保存图片', command=self.save_image)
        if Win: menubar.add_command(label='配置', command=self.open_settings)
        if Win: menubar.add_command(label='加入开机自启', command=self.startWithWindows)
        menubar.add_command(label='退出', command=root.quit)
        self.root.config(menu=menubar)
        
        # 创建主框架
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 图片显示区域
        img_frame = ttk.LabelFrame(main_frame, text='今日必应壁纸')
        img_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.img_label = ttk.Label(img_frame)
        self.img_label.pack(padx=10, pady=10)
        
        # 创建 Notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 简略信息标签页
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text='简略')
        
        # 创建信息标签
        ttk.Label(info_frame, text='日期：').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.date_label = ttk.Label(info_frame, text='')
        self.date_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(info_frame, text='标题：').grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.title_label = ttk.Label(info_frame, text='')
        self.title_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(info_frame, text='版权信息：').grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.copyright_label = ttk.Label(info_frame, text='')
        self.copyright_label.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(info_frame, text='图片 URL：').grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.url_label = ttk.Label(info_frame, text='', foreground='blue', cursor='hand2')
        self.url_label.grid(row=3, column=1, sticky='w', padx=5, pady=2)
        self.url_label.bind('<Button-1>', self.open_url)
        
        # JSON信息标签页
        json_frame = ttk.Frame(notebook)
        notebook.add(json_frame, text='JSON')
        
        # 创建JSON显示区域
        json_scroll = ttk.Scrollbar(json_frame)
        json_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.json_text = tk.Text(json_frame, wrap=tk.NONE, yscrollcommand=json_scroll.set, bg='#F0F0F0', padx=10, pady=10)
        self.json_text.pack(fill=tk.BOTH, expand=True)
        json_scroll.config(command=self.json_text.yview)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set('就绪。')
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 获取图片
        self.get_bing_image()
    
    def open_settings(self):
        '''打开配置对话框'''
        SettingsDialog(self.root)
    
    def get_bing_image(self):
        '''获取必应图片信息并显示'''
        try:
            self.status_var.set('正在获取图片信息……')
            self.root.update()
            
            response = requests.get('https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US')
            self.data = response.json()['images'][0]
            
            # 更新UI信息
            self.date_label.config(text=self.data['enddate'])
            self.title_label.config(text=self.data['title'])
            self.copyright_label.config(text=self.data['copyright'])
            
            url = 'https://www.bing.com' + self.data['url']
            self.url_label.config(text=url)
            
            # 格式化显示JSON
            formatted_json = json.dumps(self.data, indent=2, ensure_ascii=False)
            self.json_text.delete(1.0, tk.END)
            self.json_text.insert(tk.END, formatted_json)
            
            # 下载并显示图片
            self.status_var.set('正在下载图片……')
            self.root.update()
            
            img_url = url.replace('&pid=hp', '')
            img_response = requests.get(img_url)
            img_data = img_response.content
            
            # 使用PIL处理图片
            img = Image.open(BytesIO(img_data))
            
            # 缩放图片到640x360，保持宽高比
            img.thumbnail((640, 360))
            self.tk_img = ImageTk.PhotoImage(img)
            self.img_label.config(image=self.tk_img)
            
            # 保存原始图片数据
            self.original_img_data = img_data
            
            self.status_var.set('图片加载完成。')
        except Exception as e:
            messagebox.showerror('错误', f'获取图片时出错: {str(e)}')
            self.status_var.set(f'错误: {str(e)}')
    
    def save_image(self):
        '''保存图片到指定位置'''
        try:
            default_filename = f'{self.data['enddate']}.jpg'
            file_path = filedialog.asksaveasfilename(initialdir=folder_path, initialfile=default_filename, defaultextension='.jpg', filetypes=[('JPEG图片', '*.jpg')])
            
            if file_path:
                with open(file_path, 'wb') as file:
                    file.write(self.original_img_data)
                messagebox.showinfo('保存成功', f'图片已保存到 {file_path}。')
                self.status_var.set(f'图片已保存到: {file_path}。')
        except Exception as e:
            messagebox.showerror('保存错误', f'保存图片时出错: {str(e)}。')
            self.status_var.set(f'保存错误: {str(e)}。')
    
    def open_url(self, event):
        '''在浏览器中打开图片URL'''
        webbrowser.open(self.url_label.cget('text'))

    def startWithWindows(self):
        '''开机自启快捷方式添加'''
        try:
            shell = Dispatch('WScript.Shell')
            shortcut_path = os.path.join(os.path.join(os.environ['APPDATA'], 'Microsoft/Windows/Start Menu/Programs/Startup'), 'BingImageWallpaper.lnk')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = os.path.abspath(sys.argv[0])
            shortcut.Arguments = '--set-wallpaper'
            shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(sys.argv[0]))
            shortcut.save()
            messagebox.showinfo('成功', '已添加到开机自启。')
        except Exception as e: messagebox.showerror('错误', f'添加到开机自启失败: {str(e)}')

def set_wallpaper_mode():
    '''设置壁纸模式（命令行参数 --set-wallpaper 时调用）'''
    if not Win:
        messagebox.showerror('平台不支持', '欲设置壁纸，请在 Windows 平台运行。')
        return
    try:
        global folder_path, save_history
        
        # 获取图片信息
        response = requests.get('https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US')
        data = response.json()['images'][0]
        enddate = data['enddate']
        
        # 根据设置确定文件名
        filename = f'{enddate}.jpg' if save_history else 'Wallpaper.jpg'
        file_path = os.path.join(folder_path, filename)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 下载图片
        img_url = 'https://www.bing.com' + data['url']
        img_data = requests.get(img_url).content
        
        # 保存图片
        with open(file_path, 'wb') as f:
            f.write(img_data)
        
        # 设置壁纸
        ctypes.windll.user32.SystemParametersInfoW(20, 0, file_path, 3)
    except Exception as e: messagebox.showerror('无法设置壁纸', f'设置壁纸时出错: {str(e)}。')

# 处理命令行参数
if '--set-wallpaper' in sys.argv: set_wallpaper_mode()
else:
    root = tk.Tk()
    app = BingImageApp(root)
    root.mainloop()