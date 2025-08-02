import tkinter as tk, qrcode, cv2, threading
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageGrab
from pyzbar import pyzbar

# 创建主窗口
root = tk.Tk()
root.title('二维码工具')
root.resizable(False, False)

notebook = ttk.Notebook(root)
notebook.pack(pady=10, expand=True)

# 生成二维码
def generate(text: str, version: int | None = None, error_correction: int = 1, box_size: int = 10, border: int = 4):
    if not text.strip():
        messagebox.showerror('错误', '文本内容不能为空。')
        return
        
    try:
        qr = qrcode.QRCode(version=version, error_correction=error_correction, box_size=box_size, border=border)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        
        # 显示预览
        preview_window = tk.Toplevel(root)
        preview_window.title('二维码预览')
        preview_window.transient(root)
        preview_window.grab_set()
        
        tk_img = ImageTk.PhotoImage(img)
        
        # 显示图像
        img_label = tk.Label(preview_window, image=tk_img)
        img_label.image = tk_img  # 保持引用
        img_label.pack(padx=20, pady=10)
        
        # 保存按钮
        def save_image():
            file_path = filedialog.asksaveasfilename(
                defaultextension='.png',
                filetypes=[('PNG 图片', '*.png'), ('JPG 图片', '*.jpg'), ('所有文件', '*.*')]
            )
            if file_path:
                try:
                    img.save(file_path)
                    messagebox.showinfo('成功', f'二维码已保存到 {file_path}。')
                    preview_window.destroy()
                except Exception as e: messagebox.showerror('保存错误', f'保存二维码时出错：{str(e)}。')
        btn_frame = ttk.Frame(preview_window)
        btn_frame.pack(pady=10, fill=tk.X, padx=20)
        
        ttk.Button(btn_frame, text='保存二维码', command=save_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='关闭预览', command=preview_window.destroy).pack(side=tk.RIGHT, padx=5)
        
    except Exception as e: messagebox.showerror('生成错误', f'生成二维码时出错：{str(e)}。')

generate_frame = ttk.Frame(notebook)
notebook.add(generate_frame, text='生成二维码')

# 使用网格布局管理器
generate_frame.grid_columnconfigure(1, weight=1)

ttk.Label(generate_frame, text='文本内容：').grid(row=0, column=0, padx=5, pady=5, sticky='w')
text = tk.Text(generate_frame, width=50, height=5)
text.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

ttk.Label(generate_frame, text='版本（1-40, 留空自动）：').grid(row=1, column=0, padx=5, pady=5, sticky='w')
version = tk.Entry(generate_frame)
version.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
version.insert(0, '')

ttk.Label(generate_frame, text='容错级别：').grid(row=2, column=0, padx=5, pady=5, sticky='w')
error_correction = ttk.Combobox(generate_frame, values=['低 (L)', '中 (M)', '高 (Q)', '最高 (H)'], state='readonly')
error_correction.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
error_correction.current(1)

ttk.Label(generate_frame, text='二维码大小：').grid(row=3, column=0, padx=5, pady=5, sticky='w')
box_size = tk.Entry(generate_frame)
box_size.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
box_size.insert(0, '10')

ttk.Label(generate_frame, text='边框大小：').grid(row=4, column=0, padx=5, pady=5, sticky='w')
border = tk.Entry(generate_frame)
border.grid(row=4, column=1, padx=5, pady=5, sticky='ew')
border.insert(0, '4')

# 生成按钮
generate_btn = ttk.Button(generate_frame, text='生成并预览二维码', command=lambda: generate(
        text.get('1.0', 'end').strip(),
        int(version.get()) if version.get().isdigit() else None,
        [qrcode.constants.ERROR_CORRECT_L, 
         qrcode.constants.ERROR_CORRECT_M,
         qrcode.constants.ERROR_CORRECT_Q,
         qrcode.constants.ERROR_CORRECT_H][error_correction.current()],
        int(box_size.get()) if box_size.get().isdigit() else 10,
        int(border.get()) if border.get().isdigit() else 4))
generate_btn.grid(row=5, column=0, columnspan=2, pady=10)

# 扫描二维码
def scan(img):
    result.config(state=tk.NORMAL)
    result.delete('1.0', 'end')
    
    try:
        decoded_objects = pyzbar.decode(img, symbols=[pyzbar.ZBarSymbol.QRCODE])
        if decoded_objects:result.insert('1.0', decoded_objects[0].data.decode('utf-8'))
        else: result.insert('1.0', '未检测到二维码。')
    except Exception as e: result.insert('1.0', f'扫描错误：{str(e)}。')

    result.config(state=tk.DISABLED)

def open_file():
    img_path = filedialog.askopenfilename(filetypes=[('图片文件', '*.png *.jpg *.jpeg *.bmp'),('所有文件', '*.*')])
    
    if img_path:
        try:
            img = Image.open(img_path)
            scan(img)
        except Exception as e: messagebox.showerror('错误', f'无法打开图片: {str(e)}。')

def from_clipboard():
    try:
        clipboard_img = ImageGrab.grabclipboard()
        if isinstance(clipboard_img, Image.Image): scan(clipboard_img)
        else: messagebox.showerror('错误', '剪贴板中没有图片。')
    except Exception as e: messagebox.showerror('错误', f'无法读取剪贴板: {str(e)}。')

# 摄像头扫描相关变量
camera_active = False
camera_thread = camera_cap = None

def camera_scan():
    global camera_active, camera_cap
    
    # 默认使用第一个摄像头（索引0）
    camera_cap = cv2.VideoCapture(0)
    
    if not camera_cap.isOpened():
        messagebox.showerror('错误', '无法打开摄像头。')
        return
    
    camera_active = True
    camera_btn.config(text='停止扫描', command=stop_camera)
    
    def scan_frame():
        while camera_active:
            ret, frame = camera_cap.read()
            if not ret: break
            
            # 显示预览
            preview_frame = cv2.resize(frame, (320, 240))
            cv2.imshow('Preview', preview_frame)
            
            # 解码二维码
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            decoded_objects = pyzbar.decode(gray, symbols=[pyzbar.ZBarSymbol.QRCODE])
            
            if decoded_objects:
                result.config(state=tk.NORMAL)
                result.delete('1.0', 'end')
                result.insert('1.0', decoded_objects[0].data.decode('utf-8'))
                result.config(state=tk.DISABLED)
                stop_camera()
                cv2.destroyWindow('Preview')
                break
            
            # 按ESC退出
            if cv2.waitKey(1) == 27:
                stop_camera()
                cv2.destroyWindow('Preview')
                break
    
    # 启动扫描线程
    camera_thread = threading.Thread(target=scan_frame, daemon=True)
    camera_thread.start()

def stop_camera():
    global camera_active
    camera_active = False
    camera_btn.config(text='摄像头扫描', command=camera_scan)
    if camera_cap and camera_cap.isOpened():
        camera_cap.release()

def on_closing():
    stop_camera()
    cv2.destroyAllWindows()
    root.destroy()

root.protocol('WM_DELETE_WINDOW', on_closing)

# 扫描框架
scan_frame = ttk.Frame(notebook)
notebook.add(scan_frame, text='扫描二维码')

# 使用网格布局管理器
scan_frame.grid_columnconfigure(1, weight=1)

# 文件选择
ttk.Label(scan_frame, text='选择图片文件').grid(row=0, column=0, padx=5, pady=5, sticky='w')
ttk.Button(scan_frame, text='浏览', command=open_file, width=10).grid(row=0, column=1, padx=5, pady=5, sticky='w')

# 剪贴板
ttk.Label(scan_frame, text='从剪贴板读取：').grid(row=1, column=0, padx=5, pady=5, sticky='w')
ttk.Button(scan_frame, text='粘贴图片', command=from_clipboard, width=10).grid(row=1, column=1, padx=5, pady=5, sticky='w')

# 摄像头扫描按钮
camera_btn = ttk.Button(scan_frame, text='摄像头扫描', command=camera_scan)
camera_btn.grid(row=2, column=0, columnspan=2, pady=10)

# 扫描结果
ttk.Label(scan_frame, text='扫描结果：').grid(row=3, column=0, padx=5, pady=5, sticky='nw')
result = tk.Text(scan_frame, width=50, height=8, state=tk.DISABLED)
result.grid(row=3, column=1, padx=5, pady=5, sticky='nsew')

# 添加滚动条
scrollbar = ttk.Scrollbar(scan_frame, command=result.yview)
scrollbar.grid(row=3, column=2, sticky='ns')
result.config(yscrollcommand=scrollbar.set)

root.mainloop()