'''
    Copyright (c) Kendall 2025. All rights reserved.
    Last Updated: 2025/8/1
'''
import tkinter as tk, json, os, ctypes, threading, ntplib, pyttsx3, sys, psutil
from tkinter import ttk, messagebox
from datetime import datetime, timezone
from ctypes import wintypes
from tkcalendar import DateEntry

# 电源管理相关
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

class ExamTimer:
    def __init__(self, master):
        self.silent_mode = '-s' in sys.argv
        
        # 初始化配置
        self.config = self.load_config()
        self.exams = self.parse_exams()

        if not self.should_show_window():
            if master: master.destroy()
            return
        
        self.master = master
        self.master.title('考试倒计时')
        self.master.attributes('-fullscreen', True)
        self.master.protocol('WM_DELETE_WINDOW', self.on_closing)

        self.original_bg = master.cget('bg')
        self.original_time_fg = '#2E86C1'  # 初始时间文字颜色
        self.status = ''
        
        self.last_update = datetime.now()
        self.microsecond_counter = 0

        self.setup_ui()
        self.set_power_settings(True)
        threading.Thread(target = self.check_time_sync).start()
        self.update_display()
        self.self_protect()

        self.engine_lock = threading.Lock()
        self.engine = pyttsx3.init()
        self.voice_alert_sent = False
        self.last_alert_time = None
        self.progress_value = 0
        self.progress_max = 0
        self.red_screen_enabled = self.config['settings'].get('red_screen', True)

    def should_show_window(self):
        if not self.silent_mode:
            return True
        
        return len(self.exams) > 0

    def setup_ui(self):
        # 状态文本
        self.status_label = tk.Label(
            self.master, 
            font=('微软雅黑', 30),
            pady=20,
            bg=self.master.cget('bg')
        )
        self.status_label.pack()
        
        # 倒计时时间显示
        self.time_label = tk.Label(
            self.master,
            font=('DS-Digital', 100),
            fg=self.original_time_fg,
            bg=self.master.cget('bg')
        )
        self.time_label.pack()
        
        # 当前时间标签
        self.current_time = tk.Label(
            self.master,
            text='当前时间',
            font=('微软雅黑', 30),
            pady=40,
            bg=self.master.cget('bg')
        )
        self.current_time.pack()
        
        # 当前时间显示
        self.current_time_label = tk.Label(
            self.master,
            font=('DS-Digital', 100),
            fg='#28B463',
            bg=self.master.cget('bg')
        )
        self.current_time_label.pack()
        
        # 功能按钮框架
        self.button_frame = tk.Frame(self.master, bg=self.master.cget('bg'))
        self.button_frame.pack(pady=20)
        
        # 操作按钮
        self.action_button = tk.Button(
            self.button_frame,
            font=('微软雅黑', 20),
            width=10,
            bg=self.master.cget('bg'),
            fg='#000000'
        )
        self.action_button.pack(side=tk.LEFT, padx=20)
        
        # 配置按钮
        self.config_button = tk.Button(
            self.button_frame,
            text='配置',
            font=('微软雅黑', 20),
            width=10,
            bg='#F4D03F',
            command=self.show_config_dialog
        )
        self.config_button.pack(side=tk.LEFT, padx=20)

        # 进度条框架
        progress_frame = tk.Frame(self.master, bg=self.master.cget('bg'))
        progress_frame.pack(fill=tk.X, padx=50, pady=20)
        
        # 进度条
        self.progress = ttk.Progressbar(
            progress_frame,
            orient='horizontal',
            mode='determinate',
            length=600
        )
        self.progress.pack(fill=tk.X, expand=True)
        
        # 初始化进度条
        self.update_progress()

        self.copyright_label = tk.Label(
            self.master,
            text='版权所有 © Kendall 2025。保留所有权利。', 
            font=('微软雅黑', 10),
            fg='#000000',
            bg=self.master.cget('bg')
        )
        self.copyright_label.pack(side=tk.BOTTOM, pady=10)

    def load_config(self):
        '''加载完整配置文件'''
        default_config = {
            'exams': {},
            'settings': {
                'ntp_server': 'time.windows.com', 
                'voice_text': ''
            }
        }
        
        try:
            if not os.path.exists('et_config.json'):
                return default_config
                
            with open('et_config.json') as f:
                loaded = json.load(f)
                
            # 清理过期考试
            today = datetime.now().strftime('%Y-%m-%d')
            valid_exams = {
                date: subjects 
                for date, subjects in loaded.get('exams', {}).items()
                if date >= today
            }
            
            return {
                'exams': valid_exams,
                'settings': {
                    **default_config['settings'],
                    **loaded.get('settings', {})
                }
            }
            
        except Exception as e:
            messagebox.showerror('配置错误', f'加载配置失败：{str(e)}')
            return default_config

    def parse_exams(self):
        '''从配置中解析考试时间'''
        today = datetime.now().strftime("%Y-%m-%d")
        today_exams = self.config["exams"].get(today, {})

        exams = []
        # 解析考试安排
        for subject, times in today_exams.items():
            try:
                start = datetime.strptime(times[0], '%H%M').time()
                end = datetime.strptime(times[1], '%H%M').time()
                if start >= end:
                    continue
                exams.append((subject, start, end))
            except:
                continue
                
        return sorted(exams, key=lambda x: x[1])

    def save_config(self):
        '''保存完整配置'''
        try:
            # 再次清理过期数据
            today = datetime.now().strftime("%Y-%m-%d")
            self.config["exams"] = {
                date: subjects 
                for date, subjects in self.config["exams"].items()
                if date >= today
            }
            
            self.config['settings']['ntp_server'] = self.ntp_combo.get().strip()
            self.config['settings']['voice_text'] = self.voice_combo.get().strip()

            with open('et_config.json', 'w', encoding='gb18030') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            messagebox.showerror('保存失败', f'无法保存配置：{str(e)}')

    def show_config_dialog(self):
        config_window = tk.Toplevel(self.master)
        config_window.title('配置')
        config_window.resizable(False, False)
        config_window.attributes('-toolwindow', 2)
        config_window.attributes('-topmost', True)

        # 日期选择
        tk.Label(config_window, text="考试日期:", font=('微软雅黑', 14)).grid(row=0, column=0, padx=5, pady=5)
        self.date_entry = DateEntry(
            config_window, 
            locale='zh_CN', 
            date_pattern='yyyy-mm-dd',
            mindate=datetime.now().date()
        )
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 当前考试列表框架
        list_frame = tk.Frame(config_window)
        list_frame.grid(row=1, columnspan=2, pady=10, sticky='nsew')
        
        # 考试列表
        self.tree = ttk.Treeview(
            list_frame,
            columns=('date', 'subject', 'start', 'end'),
            show='headings',
            height=8
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 定义列
        columns = [
            ('date', '日期', 120),
            ('subject', '科目', 100),
            ('start', '开始时间', 100),
            ('end', '结束时间', 100)
        ]
        for col_id, col_text, width in columns:
            self.tree.heading(col_id, text=col_text, anchor=tk.CENTER)
            self.tree.column(col_id, width=width, anchor=tk.CENTER)
        
        # 列表滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 定义列
        self.tree.heading('subject', text='科目', anchor=tk.CENTER)
        self.tree.heading('start', text='开始时间', anchor=tk.CENTER)
        self.tree.heading('end', text='结束时间', anchor=tk.CENTER)
        self.tree.column('subject', width=120, anchor=tk.CENTER)
        self.tree.column('start', width=120, anchor=tk.CENTER)
        self.tree.column('end', width=120, anchor=tk.CENTER)
    
        # 科目选择（改为可编辑的输入框）
        tk.Label(config_window, text='科目:', font=('微软雅黑', 14)).grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.subject_entry = ttk.Entry(config_window, font=('微软雅黑', 14))
        self.subject_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        # 时间输入验证函数
        def validate_time(h, m):
            try:
                if h == '' or m == '': return False
                int(h), int(m)
                return 0 <= int(h) <= 23 and 0 <= int(m) <= 59
            except:
                return False

        # 开始时间
        tk.Label(config_window, text='开始时间:', font=('微软雅黑', 14)).grid(row=3, column=0, padx=5, pady=5, sticky='e')
        start_hour = ttk.Combobox(config_window, values=[f'{h:02d}' for h in range(24)], width=3)
        start_hour.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        start_min = ttk.Combobox(config_window, values=[f'{m:02d}' for m in range(0, 60, 5)], width=3)
        start_min.grid(row=3, column=1, padx=5, pady=5)
        
        # 结束时间
        tk.Label(config_window, text='结束时间:', font=('微软雅黑', 14)).grid(row=4, column=0, padx=5, pady=5, sticky='e')
        end_hour = ttk.Combobox(config_window, values=[f'{h:02d}' for h in range(24)], width=3)
        end_hour.grid(row=4, column=1, padx=5, pady=5, sticky='w')
        end_min = ttk.Combobox(config_window, values=[f'{m:02d}' for m in range(0, 60, 5)], width=3)
        end_min.grid(row=4, column=1, padx=5, pady=5)

        ntp_frame = tk.LabelFrame(config_window, text='NTP 服务器设置', font=('微软雅黑', 12))
        ntp_frame.grid(row=5, columnspan=2, pady=10, padx=10, sticky='ew')

        ntp_presets = [
            'pool.ntp.org', 
            'ntp.ntsc.ac.cn', 
            'cn.pool.ntp.org', 
            'ntp.aliyun.com', 
            'ntp.tencent.com', 
            'time.windows.com', 
            'time.cloudflare.com'
        ]

        tk.Label(ntp_frame, text='服务器：', font=('微软雅黑', 12)).grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.ntp_combo = ttk.Combobox(ntp_frame, values=ntp_presets, font=('微软雅黑', 12), width=40)
        self.ntp_combo.grid(row=0, column=1, padx=5, pady=5)
        if self.config['settings'].get('ntp_server'):
            self.ntp_combo.set(self.config['settings']['ntp_server'])

        test_btn = tk.Button(ntp_frame, text='测试', command=self.ntp_test, width=8)
        test_btn.grid(row=0, column=2, padx=5, pady=5)

        self.response_label = tk.Label(ntp_frame, text='', font=('微软雅黑', 12), anchor='w')
        self.response_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky='w')
        
        voice_frame = tk.LabelFrame(config_window, text='语音播报设置', font=('微软雅黑', 12))
        voice_frame.grid(row=6, columnspan=2, pady=10, padx=10, sticky='ew')

        text_presets = [
            '离考试结束还有十五分钟，请考生抓紧时间。', 
            ''
        ]

        tk.Label(voice_frame, text='文本：', font=('微软雅黑', 12)).grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.voice_combo = ttk.Combobox(voice_frame, values=text_presets, font=('微软雅黑', 12), width=40)
        self.voice_combo.grid(row=0, column=1, padx=5, pady=5)
        if self.config['settings'].get('voice_text'):
            self.voice_combo.set(self.config['settings']['voice_text'])

        preview_btn = tk.Button(voice_frame, text='预览', command=self.preview_voice, width=8)
        preview_btn.grid(row=0, column=2, padx=5, pady=5)

        # 红屏效果复选框
        self.red_screen_var = tk.BooleanVar(value=self.config['settings'].get('red_screen', True))
        red_screen_cb = tk.Checkbutton(
            config_window,
            text="启用当剩余时间≤15分钟时红屏",
            variable=self.red_screen_var,
            font=('微软雅黑', 12),
            anchor='w'
        )
        red_screen_cb.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
        
        # 按钮框架
        btn_frame = tk.Frame(config_window)
        btn_frame.grid(row=8, columnspan=2, pady=10)
        
        # 状态标签
        status_label = tk.Label(
            config_window, 
            text='',
            fg='#2E86C1',
            font=('微软雅黑', 12),
            wraplength=380
        )
        status_label.grid(row=9, columnspan=2, pady=5, sticky='ew')

        def update_status(text, color='#2E86C1'):
            status_label.config(text=text, fg=color)
            config_window.after(5000, lambda: status_label.config(text=''))  # 5秒后自动清除

        # 刷新考试列表
        def refresh_list():
            self.tree.delete(*self.tree.get_children())
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 按日期排序
            sorted_dates = sorted(
                self.config["exams"].keys(),
                key=lambda x: datetime.strptime(x, "%Y-%m-%d")
            )
            
            for date_str in sorted_dates:
                if date_str < today:
                    continue  # 跳过过期考试（虽然加载时已清理）
                    
                exams = self.config["exams"][date_str]
                for subject, times in exams.items():
                    start = f"{times[0][:2]}:{times[0][2:]}"
                    end = f"{times[1][:2]}:{times[1][2:]}"
                    
                    self.tree.insert('', tk.END, values=(
                        date_str,
                        subject,
                        start,
                        end
                    ))
        
        refresh_list()  # 初始加载

        def save_config():
            try:
                # 验证日期
                exam_date = self.date_entry.get_date()
                date_str = exam_date.strftime("%Y-%m-%d")

                if exam_date < datetime.now().date():
                    update_status("不能添加过去日期的考试。", '#FF0000')
                    return
                    
                # 验证输入
                subject = self.subject_entry.get().strip()
                if not subject:
                    update_status('请输入考试科目名称。', '#FF0000')
                    return
                
                # 时间验证
                if not all([validate_time(start_hour.get(), start_min.get()),
                       validate_time(end_hour.get(), end_min.get())]):
                    update_status('时间格式无效 (应为00:00-23:59)。', '#FF0000')
                    return
                
                # 解析时间
                start_time = f'{start_hour.get()}{start_min.get()}'
                end_time = f'{end_hour.get()}{end_min.get()}'
                start_dt = datetime.strptime(start_time, '%H%M')
                end_dt = datetime.strptime(end_time, '%H%M')

                # 验证时间顺序
                if start_dt >= end_dt:
                    update_status('开始时间必须早于结束时间。', '#FF0000')
                    return

                date_str = exam_date.strftime('%Y-%m-%d')
                if date_str not in self.config['exams']:
                    self.config['exams'][date_str] = {}
                self.config['exams'][date_str][subject] = [start_time, end_time]

                self.config['settings']['red_screen'] = self.red_screen_var.get()
                self.red_screen_enabled = self.config['settings']['red_screen']
        
                # 保存配置
                self.save_config()

                update_status('已保存。', '#28B463')
                self.exams = self.parse_exams()
                self.update_display()
                refresh_list()
            except Exception as e:
                update_status(f'{str(e)}', '#FF0000')

        # 添加删除按钮
        del_button = tk.Button(
            btn_frame,
            text='删除选中',
            command=lambda: delete_selected(),
            width=10
        )
        del_button.pack(side=tk.LEFT, padx=5)

        def delete_selected():
            selected = self.tree.selection()
            if not selected:
                update_status('请先选择要删除的考试。', '#FF0000')
                return
                
            # 创建配置副本避免修改迭代对象
            config_copy = self.config["exams"].copy()
        
            # 遍历所有选中的条目
            for item in selected:
                values = self.tree.item(item, 'values')
                if len(values) < 4:
                    continue
                    
                date_str = values[0]
                subject = values[1]
                
                # 删除对应条目
                if date_str in config_copy:
                    if subject in config_copy[date_str]:
                        del config_copy[date_str][subject]
                        
                    # 清理空日期条目
                    if not config_copy[date_str]:
                        del config_copy[date_str]

            # 更新配置并保存
            self.config["exams"] = config_copy
            self.save_config()
            
            update_status('已删除选中考试。', '#28B463')
            self.exams = self.parse_exams()
            self.update_display()
            refresh_list()
        
        tk.Button(btn_frame, text='保存', command=save_config, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text='退出', command=config_window.destroy, width=10).pack(side=tk.RIGHT, padx=10)

    def find_current_exam(self, now_time):
        current_date = datetime.now().date()
        current_datetime = datetime.combine(current_date, now_time)
        
        for subject, start, end in self.exams:
            start_dt = datetime.combine(current_date, start)
            end_dt = datetime.combine(current_date, end)
            
            if start_dt <= current_datetime < end_dt:
                return ('ongoing', subject, end_dt)
            
            if current_datetime < start_dt:
                return ('upcoming', subject, start_dt)
        
        return ('finished', None, None)

    def update_display(self):
        now = datetime.now()
        current_datetime = now
        
        # 计算精确到0.1秒的时间差
        delta = now - self.last_update
        self.last_update = now
        self.microsecond_counter += delta.microseconds
        
        # 更新进度条
        self.update_progress()
        
        # 每0.1秒更新一次
        if self.microsecond_counter >= 100000:  # 100,000微秒=0.1秒
            self.microsecond_counter = 0
            
            # 获取当前时间（精确到0.1秒）
            current_time = now.time()
            frac_second = now.microsecond // 100000  # 获取0.1秒部分
            
            # 更新当前时间显示
            current_time_str = now.strftime("%H:%M:%S") + f".{frac_second}"
            self.current_time_label.config(text=current_time_str)
            
            # 更新考试状态
            status, subject, target_time = self.find_current_exam(current_time)
            self.status = status
            
            # 倒计时显示
            if status == 'ongoing':
                time_left = target_time - now
                total_seconds = time_left.total_seconds()
                
                # 格式化倒计时时间（精确到0.1秒）
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)
                frac_seconds = int(10 * (total_seconds - int(total_seconds)))
                
                time_left_str = f"{hours:02}:{minutes:02}:{seconds:02}.{frac_seconds}"
                self.time_label.config(text=time_left_str)

                self.status_label.config(text=f'{subject}考试还剩')
                self.action_button.config(
                    text='正在考试',
                    state=tk.DISABLED,
                    command=None
                )
                self.config_button.config(state=tk.DISABLED)
                
                # 15分钟背景变红
                if self.red_screen_enabled and total_seconds <= 900:
                    self.master.configure(bg='#FF0000')
                    self.update_child_bg('#FF0000')
                    self.time_label.config(fg='#FFFFFF')

                if 0 < total_seconds <= 900:
                    should_alert = (
                        not self.voice_alert_sent and 
                        total_seconds <= 900 and
                        (self.last_alert_time is None or 
                        (datetime.now() - self.last_alert_time).total_seconds() > 60)
                    )
                    if should_alert:
                        self.trigger_voice_alert()
                        self.voice_alert_sent = True
                        self.last_alert_time = datetime.now()
            elif status == 'upcoming':
                time_until = target_time - now
                total_seconds = time_until.total_seconds()
                
                # 格式化倒计时时间
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)
                frac_seconds = int(10 * (total_seconds - int(total_seconds)))
                
                time_until_str = f"{hours:02}:{minutes:02}:{seconds:02}.{frac_seconds}"
                self.time_label.config(text=time_until_str)
                
                time_until = target_time - current_datetime
                self.status_label.config(text=f'{subject}考试还有')
                self.action_button.config(
                    text='最小化',
                    state=tk.NORMAL,
                    command=self.master.iconify
                )

                # 重置背景
                self.master.configure(bg=self.original_bg)
                self.update_child_bg(self.original_bg)
                self.time_label.config(fg=self.original_time_fg)
                self.status_label.config(fg='#000000')
                self.current_time.config(fg='#000000')
                self.config_button.config(state=tk.NORMAL)

            else:
                # 重置状态
                self.time_label.config(text="00:00:00.0")
                self.voice_alert_sent = False
                self.status_label.config(text='今日已没有考试')
                self.action_button.config(
                    text='关闭',
                    state=tk.NORMAL,
                    command=self.on_closing
                )
                self.master.configure(bg=self.original_bg)
                self.update_child_bg(self.original_bg)
                self.time_label.config(fg=self.original_time_fg)
                self.status_label.config(fg='#000000')
                self.current_time.config(fg='#000000')
                self.config_button.config(state=tk.NORMAL)

        self.master.after(50, self.update_display)

    def update_progress(self):
        """根据考试状态更新进度条"""
        now = datetime.now().time()
        current_datetime = datetime.now()
        
        status, subject, target_time = self.find_current_exam(now)
        
        if status == 'ongoing':
            # 计算考试总时长（分钟）
            start_dt = datetime.combine(current_datetime.date(), self.get_subject_start_time(subject))
            end_dt = datetime.combine(current_datetime.date(), self.get_subject_end_time(subject))
            total_duration = (end_dt - start_dt).total_seconds() / 60
            
            # 计算已进行时间比例
            elapsed = (current_datetime - start_dt).total_seconds() / 60
            progress = 100 - min(100, max(0, (elapsed / total_duration) * 100))
            
            self.progress['value'] = progress
            self.progress['maximum'] = 100
            
        else:
            # 非考试状态进度条为0
            self.progress['value'] = 0

    def update_child_bg(self, color):
        '''更新所有子组件背景颜色'''
        widgets = [
            self.status_label, 
            self.time_label,
            self.current_time_label,
            self.current_time,
            self.action_button, 
            self.button_frame,
            self.copyright_label
        ]
        for widget in widgets:
            widget.config(bg=color)

    def get_subject_start_time(self, subject_name):
        """获取指定科目的开始时间"""
        today = datetime.now().strftime("%Y-%m-%d")
        exams = self.config["exams"].get(today, {})
        subject_data = exams.get(subject_name, [])
        if subject_data:
            return datetime.strptime(subject_data[0], "%H%M").time()
        return datetime.now().time()  # 默认值

    def get_subject_end_time(self, subject_name):
        """获取指定科目的结束时间"""
        today = datetime.now().strftime("%Y-%m-%d")
        exams = self.config["exams"].get(today, {})
        subject_data = exams.get(subject_name, [])
        if subject_data:
            return datetime.strptime(subject_data[1], "%H%M").time()
        return datetime.now().time()  # 默认值
    
    def set_power_settings(self, enable):
        kernel32 = ctypes.WinDLL('kernel32', use_last_error = True)
        if enable:
            state = ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        else:
            state = ES_CONTINUOUS
        kernel32.SetThreadExecutionState.restype = wintypes.DWORD
        kernel32.SetThreadExecutionState(state)

    def check_time_sync(self):
        ntp_server = self.config['settings']['ntp_server']
        try:
            client = ntplib.NTPClient()

            response = client.request(ntp_server, timeout = 3)

            ntp_time = datetime.fromtimestamp(response.tx_time, tz = timezone.utc).astimezone()
            system_time = datetime.now().astimezone()

            delta = ntp_time - system_time
            delta_seconds = delta.total_seconds()

            if abs(delta_seconds) > 5:
                system_str = system_time.strftime('%Y-%m-%d %H:%M:%S')
                ntp_str = ntp_time.strftime('%Y-%m-%d %H:%M:%S')

                diff_desc = (
                    '慢' if delta_seconds > 0
                    else '快'
                )

                messagebox.showwarning(
                    '时间不同步', 
                    '你的系统时间与世界时不同步。\n\n'
                    f'系统时间：{system_str}\n'
                    f'世界时：{ntp_str}\n'
                    f'你的时间{diff_desc}了{abs(delta_seconds)}秒。'
                )
        except Exception as e:
            messagebox.showerror('无法对时', f'对时过程中发生异常。\n{e}')

    def ntp_test(self):
        ntp_server = self.ntp_combo.get()
        if not ntp_server:
            return

        def test():
            try:
                client = ntplib.NTPClient()
                response = client.request(ntp_server, timeout = 3)
                time = datetime.fromtimestamp(response.tx_time, tz = timezone.utc).astimezone()
                str = time.strftime('%Y-%m-%d %H:%M:%S')
                self.response_label.config(text=f'来自 {ntp_server} 的响应：{str}\n其时间戳为：{response.tx_time}', fg='#28B463')
            except Exception as e:
                self.response_label.config(text=f'{ntp_server} 没有响应。\n{e}', fg='#FF0000')

        threading.Thread(target=test, daemon=True).start()

    def preview_voice(self):
        text = self.voice_combo.get()
        if not text:
            return

        def generate_and_play():
            with self.engine_lock:
                self.engine.say(text)
                self.engine.runAndWait()
                self.engine.stop()

        threading.Thread(target=generate_and_play, daemon=True).start()

    def trigger_voice_alert(self):
        text = self.config['settings'].get('voice_text')
        if not text:
            return
        
        if hasattr(self, '_active_voice_thread') and self._active_voice_thread.is_alive():
            return

        def speak():
            with self.engine_lock:
                self.engine.say(text)
                self.engine.runAndWait()
                self.engine.stop()
            del self._active_voice_thread

        self._active_voice_thread = threading.Thread(target=speak, daemon=True)
        self._active_voice_thread.start()

    def self_protect(self):
        if not ctypes.windll.shell32.IsUserAnAdmin():
            messagebox.showwarning('没有管理员权限', '请以管理员身份运行程序。')
            return
        processes = psutil.process_iter()
        for process in processes:
            if process.name().lower() == 'taskmgr.exe':
                process.kill()
                break
        self.master.after(1000, self.self_protect)

    def on_closing(self):
        if self.status == 'finished':
            self.set_power_settings(False)
            self.master.destroy()

root = tk.Tk()
app = ExamTimer(root)
root.mainloop()