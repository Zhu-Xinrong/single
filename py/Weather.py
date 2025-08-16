'''
    天气数据来自 Weather API
    Copyright (c) Kendall 2025. All rights reserved.
    Last Updated: 2025/8/9
'''
import tkinter as tk,  requests, os, time, json, sys, threading, pystray
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from io import BytesIO
from urllib.parse import urlparse
from pystray import MenuItem as item
from PIL import Image as PILImage
from win32com.client import Dispatch

# 配置默认值
DEFAULT_CONFIG = {
    "API_KEY": "",
    "LOCATION": "",
    "centigrade": True,
    "widget_position": [0, 0],
    "show_widget": True
}

class ConfigManager:
    """配置文件管理类"""
    def __init__(self, filename='weather_config.json'):
        self.filename = filename
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f: return json.load(f)
            except:
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """保存配置文件"""
        with open(self.filename, 'w') as f: json.dump(self.config, f, indent=2)
    
    def get(self, key):
        """获取配置值"""
        return self.config.get(key, DEFAULT_CONFIG.get(key))
    
    def set(self, key, value):
        """设置配置值"""
        self.config[key] = value
        self.save_config()

class WeatherService:
    """天气服务类，处理数据获取和缓存"""
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.ICON_CACHE_DIR = './weather_icons/'
        os.makedirs(self.ICON_CACHE_DIR, exist_ok=True)
        self.current_weather_data = None
        self.last_refresh_time = 0
    
    def refresh_current_weather(self):
        """刷新当前天气数据"""
        try:
            self.current_weather_data = self.get_current_weather()
            self.last_refresh_time = time.time()
            return self.current_weather_data
        except Exception as e: raise RuntimeError(f'刷新天气数据失败: {e}。')
    
    def get_current_weather(self, force_refresh=False):
        """获取当前天气数据"""
        if force_refresh or self.current_weather_data is None or time.time() - self.last_refresh_time > 900:
            try:
                url = f'https://api.weatherapi.com/v1/current.json?key={self.get_api_key()}&q={self.get_location()}&aqi=yes'
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                return response.json()
            except Exception as e: raise RuntimeError(f'获取天气数据失败: {e}。')
        else: return self.current_weather_data
        
    def get_astronomy_data(self):
        """获取天文数据"""
        try:
            url = f'https://api.weatherapi.com/v1/astronomy.json?key={self.get_api_key()}&q={self.get_location()}'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e: raise RuntimeError(f'获取天文数据失败: {e}。')
    
    def get_forecast_data(self):
        """获取预报数据"""
        try:
            url = f'https://api.weatherapi.com/v1/forecast.json?key={self.get_api_key()}&q={self.get_location()}&days=3'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e: raise RuntimeError(f'获取预报数据失败: {e}。')
    
    def get_cached_icon(self, url):
        """获取缓存的天气图标"""
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        cache_path = os.path.join(self.ICON_CACHE_DIR, filename)
        
        if not os.path.exists(cache_path):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                with open(cache_path, 'wb') as f: f.write(response.content)
            except: return None
        return cache_path
    
    def get_api_key(self):
        return self.config_manager.get("API_KEY")
    
    def get_location(self):
        return self.config_manager.get("LOCATION")
    
    def is_centigrade(self):
        return self.config_manager.get("centigrade")

class WeatherWidget:
    """天气小组件窗口"""
    def __init__(self, master, config_manager, weather_service, tray_icon):
        self.config_manager = config_manager
        self.weather_service = weather_service
        self.tray_icon = tray_icon
        self.window = tk.Toplevel(master) if master else tk.Tk()
        self.window.withdraw()  # 初始隐藏
        
        # 设置窗口位置
        pos = self.config_manager.get("widget_position")
        self.window.geometry(f'155x155+{pos[0]}+{pos[1]}')
        
        self._setup_window()
        self._create_widgets()
        self._bind_events()
        self.refresh_data()
        
        # 如果配置中显示小组件则显示窗口
        if self.config_manager.get("show_widget"): self.window.deiconify()

        self._schedule_refresh()  # 启动定时刷新
    
    def _setup_window(self):
        """配置窗口属性"""
        self.window.title('天气小组件')
        self.window.overrideredirect(True)  # 无边框
        self.window.configure(bg='#F0F0F0')
        self.window.protocol("WM_DELETE_WINDOW", self.hide_widget)
    
    def hide_widget(self):
        """隐藏小组件窗口并更新配置"""
        self.window.withdraw()
        self.config_manager.set("show_widget", False)
    
    def show_widget(self):
        """显示小组件窗口并更新配置"""
        self.window.deiconify()
        self.config_manager.set("show_widget", True)
    
    def _create_widgets(self):
        """创建界面组件"""
        # 天气图标
        self.icon_label = ttk.Label(self.window)
        self.icon_label.pack(pady=(5, 0))
        
        # 温度显示
        self.temp_label = ttk.Label(
            self.window,
            font=('Segoe UI', 20, 'bold'),
            foreground='black',
            cursor='hand2',
            background='#F0F0F0'
        )
        self.temp_label.pack()
        
        # 天气描述
        self.condition_label = ttk.Label(
            self.window,
            font=('Segoe UI', 9),
            foreground='black',
            wraplength=140,
            background='#F0F0F0'
        )
        self.condition_label.pack()
        
        # 更新时间
        self.update_label = ttk.Label(
            self.window,
            font=('Segoe UI', 7),
            foreground='black',
            background='#F0F0F0'
        )
        self.update_label.pack(pady=(0, 5))
    
    def _bind_events(self):
        """绑定事件"""
        self.window.bind('<ButtonPress-1>', self._start_drag)
        self.window.bind('<B1-Motion>', self._on_drag)
        self.temp_label.bind('<Button-1>', self._toggle_units)
    
    def _start_drag(self, event):
        """开始拖动"""
        self._drag_data = {'x': event.x, 'y': event.y}
    
    def _on_drag(self, event):
        """处理拖动事件"""
        x = self.window.winfo_x() - self._drag_data['x'] + event.x
        y = self.window.winfo_y() - self._drag_data['y'] + event.y
        self.window.geometry(f'+{x}+{y}')
        # 保存新位置
        self.config_manager.set("widget_position", [x, y])
    
    def _toggle_units(self, event=None):
        """切换温度单位"""
        centigrade = not self.weather_service.is_centigrade()
        self.config_manager.set("centigrade", centigrade)
        self._update_display()
    
    def _update_display(self):
        """更新显示内容"""
        if hasattr(self, 'temp_c') and hasattr(self, 'temp_f'):
            if self.weather_service.is_centigrade(): temp = f"{self.temp_c:.1f}℃"
            else: temp = f"{self.temp_f:.1f}℉"
            self.temp_label.config(text=temp)
        
        if hasattr(self, 'condition_text'): self.condition_label.config(text=self.condition_text)
        
        if hasattr(self, 'last_update'): self.update_label.config(text=f"更新: {self.last_update}")
    
    def _schedule_refresh(self):
        """安排下一次刷新"""
        self.window.after(900000, self._auto_refresh)  # 15分钟 = 900,000毫秒
    
    def _auto_refresh(self):
        """自动刷新数据"""
        self.refresh_data()
        self._schedule_refresh()

    def refresh_data(self):
        """获取最新天气数据"""
        try:
            # 强制刷新服务层数据
            weather_data = self.weather_service.refresh_current_weather()
            data = weather_data['current']
            
            # 解析数据
            self.temp_c = data['temp_c']
            self.temp_f = data['temp_f']
            self.condition_text = data['condition']['text']
            self.last_update = time.strftime('%H:%M:%S')
            
            # 加载图标
            icon_url = 'https:' + data['condition']['icon']
            cached_path = self.weather_service.get_cached_icon(icon_url)
            
            if cached_path: image = Image.open(cached_path)
            else:
                response = requests.get(icon_url, timeout=10)
                image = Image.open(BytesIO(response.content))
            
            image = image.resize((64, 64), Image.LANCZOS)
            self.icon_image = ImageTk.PhotoImage(image)
            self.icon_label.config(image=self.icon_image)
            
            self._update_display()
            
            # 更新托盘图标
            if self.tray_icon: self.tray_icon.update_icon(image)
            
        except Exception as e:
            self.condition_label.config(text=f"错误: {str(e)[:15]}{'……' if len(str(e)) > 15 else ''}", foreground='red')
            self.update_label.config(text=f'最后尝试: {time.strftime("%H:%M:%S")}')
            
            # 使用默认图标更新托盘
            if self.tray_icon:
                try:
                    default_icon = Image.open("Weather_Icon.ico")
                    self.tray_icon.update_icon(default_icon)
                except: pass

class WeatherApp:
    """主天气应用窗口"""
    def __init__(self, master, config_manager, weather_service):
        self.root = master
        self.config_manager = config_manager
        self.weather_service = weather_service
        self.root.title('天气信息')
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.root.withdraw)
        
        # 创建菜单栏
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # 文件菜单
        self.menubar.add_command(label='刷新', command=self.refresh_data)
        self.menubar.add_command(label='设置', command=self.show_settings)
        self.menubar.add_command(label='加入开机自启', command=start_with_Windows)
                
        # 初始化界面
        self.create_notebook()
        self.create_loading_overlay()
        self.refresh_data()
        self._schedule_refresh()  # 启动定时刷新
    
    def create_loading_overlay(self):
        """创建加载提示"""
        self.loading_frame = ttk.Frame(self.root)
        self.loading_label = ttk.Label(
            self.loading_frame,
            text="正在加载天气数据……",
            font=("Segoe UI", 14),
            background="#ffffff",
            relief="raised",
            padding=20
        )
        self.loading_label.pack(expand=True)
        self.loading_frame.place(relx=0.5, rely=0.5, anchor="center")
    
    def show_loading(self):
        """显示加载提示"""
        self.loading_frame.lift()
        self.root.update()
    
    def hide_loading(self):
        """隐藏加载提示"""
        self.loading_frame.lower()
        self.root.update()
    
    def create_notebook(self):
        """创建标签页"""
        self.notebook = ttk.Notebook(self.root)
        
        # 当前天气标签页
        self.current_tab = ttk.Frame(self.notebook)
        self.create_current_tab()
        self.notebook.add(self.current_tab, text='当前天气')
        
        # 天文信息标签页
        self.astronomy_tab = ttk.Frame(self.notebook)
        self.create_astronomy_tab()
        self.notebook.add(self.astronomy_tab, text='天文信息')
        
        self.notebook.pack(expand=True, fill='both')
    
    def create_current_tab(self):
        """创建当前天气标签页"""
        self.current_main_frame = ttk.Frame(self.current_tab, padding=20)
        self.current_main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 位置信息
        self.location_label = ttk.Label(
            self.current_main_frame,
            font=('Segoe UI', 10),
            anchor=tk.CENTER
        )
        self.location_label.pack(pady=5)
        
        # 天气图标
        self.weather_icon = ttk.Label(self.current_main_frame)
        self.weather_icon.pack(pady=10)
        
        # 温度显示
        self.temp_label = ttk.Label(
            self.current_main_frame,
            font=('Segoe UI', 30, 'bold'),
            cursor='hand2'
        )
        self.temp_label.pack(pady=5)
        self.temp_label.bind('<Button-1>', self.toggle_units)
        
        # 天气状况
        self.condition_label = ttk.Label(self.current_main_frame, font=('Segoe UI', 15))
        self.condition_label.pack()
        
        # 详细信息框架
        self.details_frame = ttk.Frame(self.current_main_frame)
        self.details_frame.pack(pady=20, anchor='center')
        
        # 左侧信息列
        self.column1 = ttk.Frame(self.details_frame)
        self.column1.grid(row=0, column=0, padx=10)
        
        # 右侧信息列
        self.column2 = ttk.Frame(self.details_frame)
        self.column2.grid(row=0, column=1, padx=10)
        
        air_labels = [
            ('空气质量', 'us-epa-index', '', self.get_epa_index_description, self.get_epa_index_color),
            ('一氧化碳(CO)', 'co', 'µg/m³', None, None),
            ('二氧化氮(NO₂)', 'no2', 'µg/m³', None, None),
            ('臭氧(O₃)', 'o3', 'µg/m³', None, None),
            ('二氧化硫(SO₂)', 'so2', 'µg/m³', None, None),
            ('PM2.5', 'pm2_5', 'µg/m³', None, None),
            ('PM10', 'pm10', 'µg/m³', None, None)
        ]
        
        self.air_labels = {}
        for i, (label_text, key, unit, formatter, color_func) in enumerate(air_labels):
            ttk.Label(self.column2, text=label_text).grid(row=i, column=0, sticky='e')
            value_label = ttk.Label(self.column2)
            value_label.grid(row=i, column=1, sticky='w')
            self.air_labels[key] = (value_label, unit, formatter, color_func)    

    def create_astronomy_tab(self):
        """创建天文信息标签页"""
        self.astro_main_frame = ttk.Frame(self.astronomy_tab, padding=20)
        self.astro_main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 天文数据布局
        astro_items = [
            ('日出', 'sunrise'),
            ('日落', 'sunset'),
            ('月出', 'moonrise'),
            ('月落', 'moonset'),
            ('月相', 'moon_phase'),
            ('月光照明', 'moon_illumination'),
            ('月亮可见', 'is_moon_up'),
            ('太阳可见', 'is_sun_up')
        ]
        
        self.astro_labels = {}
        for i, (label_text, key) in enumerate(astro_items):
            ttk.Label(self.astro_main_frame, text=label_text).grid(row=i, column=0, sticky='e', padx=10, pady=2)
            value_label = ttk.Label(self.astro_main_frame)
            value_label.grid(row=i, column=1, sticky='w', pady=2)
            self.astro_labels[key] = value_label

    def get_epa_index_description(self, index):
        """空气质量指数描述"""
        return {
            1: '优',
            2: '良',
            3: '轻度污染',
            4: '中度污染',
            5: '重度污染',
            6: '严重污染'
        }.get(index, '未知')
    
    def get_epa_index_color(self, index):
        """空气质量指数颜色，前者为文字颜色，后者为取反色的背景颜色
        前景色参考《环境空气质量指数（AQI）技术规定（试行）》（HJ 633—2012）（https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/jcffbz/201203/W020250407406362045613.pdf）
        """
        return {
            1: ['#00E400', '#FF1BFF'], 
            2: ['#FFFF00', '#0000FF'], 
            3: ['#FF7E00', '#0081FF'], 
            4: ['#FF0000', '#00FFFF'], 
            5: ['#99004C', '#66FFB3'],  
            6: ['#7E0023', '#81FFDC']
        }.get(index, 'black')
    
    def _schedule_refresh(self):
        """安排下一次刷新"""
        self.root.after(90_0000, self._auto_refresh)  # 15分钟 = 90,0000毫秒
    
    def _auto_refresh(self):
        """自动刷新数据"""
        self.refresh_data()
        self._schedule_refresh()
    
    def refresh_data(self, event=None):
        """刷新天气数据"""
        self.show_loading()
        try:
            # 强制刷新服务层数据
            weather_data = self.weather_service.refresh_current_weather()
            location = weather_data['location']
            current = weather_data['current']
            labels = [
                ('风速', 'wind_kph', 'km/h'),
                ('湿度', 'humidity', '%'),
                ('体感温度', 'feelslike_c', '℃' if WeatherService.is_centigrade(self) else '℉'),
                ('风向角度', 'wind_degree', '°'),
                ('风向', 'wind_dir', ''),
                ('露点', 'dewpoint_c', '℃' if WeatherService.is_centigrade(self) else '℉'),
                ('能见度', 'vis_km', 'km'),
                ('紫外线指数', 'uv', '')
            ]
            
            self.current_labels = {}
            for i, (label_text, key, unit) in enumerate(labels):
                ttk.Label(self.column1, text=label_text).grid(row=i, column=0, sticky='e')
                value_label = ttk.Label(self.column1)
                value_label.grid(row=i, column=1, sticky='w')
                self.current_labels[key] = (value_label, unit)
            
            # 更新位置信息
            self.location_label.config(
                text=f"{location['name']}, {location['region']}, {location['country']}\n"
                     f"时区: {location['tz_id']}\n"
                     f"更新时间: {location['localtime']}")
            
            # 更新温度显示
            centigrade = self.weather_service.is_centigrade()
            temp = current['temp_c'] if centigrade else current['temp_f']
            unit = '℃' if centigrade else '℉'
            self.temp_label.config(text=f"{temp:.1f}{unit}")
            
            # 更新天气状况
            self.condition_label.config(text=current['condition']['text'])
            
            # 加载天气图标
            icon_url = 'https:' + current['condition']['icon']
            cached_path = self.weather_service.get_cached_icon(icon_url)
            
            try:
                if cached_path: image = Image.open(cached_path)
                else:
                    response = requests.get(icon_url, timeout=10)
                    image = Image.open(BytesIO(response.content))
            except: image = Image.new('RGB', (64, 64), (200, 200, 200))  # 灰色占位图
            
            photo = ImageTk.PhotoImage(image)
            self.weather_icon.config(image=photo)
            self.weather_icon.image = photo
            # 更新详细信息
            for key, (label, unit) in self.current_labels.items():
                value = current.get(key, 'N/A')
                if key == 'feelslike_c' and not centigrade: value = current['feelslike_f']
                elif key == 'dewpoint_c' and not centigrade: value = current['dewpoint_f']
                
                if isinstance(value, float): label.config(text=f"{value:.1f}{unit}")
                else: label.config(text=f"{value}{unit}")
            
            # 更新空气质量信息
            air_quality = current.get('air_quality', {})
            for key, (label, unit, formatter, color_func) in self.air_labels.items():
                value = air_quality.get(key, 'N/A')
                
                if formatter:
                    text = formatter(value)
                    label.config(text=text)
                else:
                    if isinstance(value, float): label.config(text=f"{value:.1f}{unit}")
                    else: label.config(text=f"{value}{unit}")
                
                if color_func: label.config(foreground=color_func(value)[0], background=color_func(value)[1], font=('Segoe UI', 10, 'bold'))
            
            # 获取天文数据
            astronomy_data = self.weather_service.get_astronomy_data()
            astro = astronomy_data['astronomy']['astro']
            
            # 更新天文信息
            for key, label in self.astro_labels.items():
                value = astro.get(key, 'N/A')
                if key == 'moon_illumination': label.config(text=f"{value}%")
                elif key in ['is_moon_up', 'is_sun_up']: label.config(text='是' if value == 1 else '否')
                else: label.config(text=value)
            
            self.hide_loading()
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("错误", f"获取天气数据失败: {str(e)}。")
    
    def toggle_units(self, event=None):
        """切换温度单位"""
        centigrade = not self.weather_service.is_centigrade()
        self.config_manager.set("centigrade", centigrade)
        self.refresh_data()
    
    def show_settings(self):
        """显示设置对话框"""
        settings = tk.Toplevel(self.root)
        settings.title("设置")
        settings.resizable(False, False)
        settings.transient(self.root)
        settings.focus_set()
        settings.grab_set()
        
        ttk.Label(settings, text="密钥：").pack(pady=(10, 0), padx=10, anchor='w')
        api_key_var = tk.StringVar(value=self.config_manager.get("API_KEY"))
        api_key_entry = ttk.Entry(settings, textvariable=api_key_var, width=40)
        api_key_entry.pack(padx=10, fill='x')
        
        ttk.Label(settings, text="位置：").pack(pady=(10, 0), padx=10, anchor='w')
        location_var = tk.StringVar(value=self.config_manager.get("LOCATION"))
        location_entry = ttk.Entry(settings, textvariable=location_var, width=40)
        location_entry.pack(padx=10, fill='x')
        
        centigrade_var = tk.BooleanVar(value=self.config_manager.get("centigrade"))
        ttk.Checkbutton(settings, text="使用摄氏度", variable=centigrade_var).pack(pady=(10, 0), padx=10, anchor='w')
        
        show_widget_var = tk.BooleanVar(value=self.config_manager.get("show_widget"))
        ttk.Checkbutton(settings, text="显示小组件（重启后生效）", variable=show_widget_var).pack(pady=(10, 0), padx=10, anchor='w')
        
        def save_settings():
            self.config_manager.set("API_KEY", api_key_var.get())
            self.config_manager.set("LOCATION", location_var.get())
            self.config_manager.set("centigrade", centigrade_var.get())
            self.config_manager.set("show_widget", show_widget_var.get())
            
            # 刷新数据
            self.refresh_data()
            if hasattr(self, 'widget'): self.widget.refresh_data()
            
            settings.destroy()
            messagebox.showinfo("成功", "设置已保存并应用。")
        
        ttk.Button(settings, text="保存", command=save_settings).pack(pady=20)

class TrayIconManager:
    """系统托盘图标管理"""
    def __init__(self, app, config_manager, weather_service):
        self.app = app
        self.config_manager = config_manager
        self.weather_service = weather_service
        self.icon = None
        self.current_icon = None
        
        # 创建默认图标
        self.default_icon = self.create_default_icon()
        self.update_icon(self.default_icon)
        
        # 启动托盘图标
        self.start_tray_icon()
    
    def create_default_icon(self):
        """创建默认托盘图标"""
        img = PILImage.new('RGB', (64, 64), (70, 130, 180))
        return img
    
    def update_icon(self, image):
        """更新托盘图标"""
        self.current_icon = image
        if self.icon: self.icon.icon = image
    
    def start_tray_icon(self):
        """启动系统托盘图标"""
        # 创建菜单
        menu = (
            item('显示详情', self.show_main_app),
            item('退出', self.exit_app)
        )
        
        # 创建托盘图标
        self.icon = pystray.Icon(
            "weather_app",
            self.current_icon,
            "天气信息",
            menu
        )
        
        # 在单独的线程中运行
        threading.Thread(target=self.icon.run, daemon=True).start()
    
    def show_main_app(self):
        """显示主应用窗口"""
        if self.app and self.app.root:
            self.app.root.deiconify()
            self.app.root.lift()
    
    def exit_app(self):
        """退出应用程序"""
        if self.app and self.app.root: self.app.root.destroy()
        self.icon.stop()
        os._exit(0)

class Application:
    """主应用类"""
    def __init__(self):
        # 创建根窗口但先隐藏
        self.root = tk.Tk()
        self.root.withdraw()
        
        # 初始化配置管理
        self.config_manager = ConfigManager()
        
        # 初始化天气服务
        self.weather_service = WeatherService(self.config_manager)
        
        # 初始化主应用窗口
        self.weather_app = WeatherApp(self.root, self.config_manager, self.weather_service)
        
        # 初始化小组件
        self.weather_widget = WeatherWidget(
            self.root, 
            self.config_manager, 
            self.weather_service,
            None  # 将在下面设置
        )
        
        # 初始化托盘图标（需要小组件实例）
        self.tray_icon = TrayIconManager(
            self.weather_app, 
            self.config_manager, 
            self.weather_service
        )
        
        # 将托盘图标管理器传递给小组件
        self.weather_widget.tray_icon = self.tray_icon
        
        # 检查启动参数
        if "-s" not in sys.argv: self.root.deiconify()

        # 启动主循环
        self.root.mainloop()

def start_with_Windows():
    '''开机自启快捷方式添加'''
    try:
        shell = Dispatch('WScript.Shell')
        shortcut_path = os.path.join(os.path.join(os.environ['APPDATA'], 'Microsoft/Windows/Start Menu/Programs/Startup'), 'Weather.lnk')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = os.path.abspath(sys.argv[0])
        shortcut.Arguments = '-s'
        shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(sys.argv[0]))
        shortcut.save()
        messagebox.showinfo('成功', '已添加到开机自启。')
    except Exception as e: messagebox.showerror('错误', f'添加到开机自启失败: {str(e)}。')

app = Application()