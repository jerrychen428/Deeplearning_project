# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 21:47:58 2025

@author: jerry

requirements.txt
opencv-python
easyocr
torch
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog, colorchooser, Menu, Toplevel, StringVar
from ttkbootstrap import Style
from PIL import Image, ImageDraw, ImageTk
import easyocr
import torch
import os
import json
import subprocess
import threading  # 導入 threading 模組

# 初始化 EasyOCR 模型
reader = easyocr.Reader(['en', 'ch_sim'], gpu=torch.cuda.is_available())

# 從圖片中檢測文本框並識別文字-
def detect_and_recognize_text(image_path):
    results = reader.readtext(image_path)
    return results

# 可視化檢測和識別結果
def visualize_results(image_path, results, output_path="output_with_boxes.jpg"):
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    
    for bbox, text, prob in results:
        x_min, y_min = bbox[0]
        x_max, y_max = bbox[2]
        draw.rectangle([x_min, y_min, x_max, y_max], outline="red", width=2)
        draw.text((x_min, y_min - 10), f"{text} ({prob:.2f})", fill="red")
    
    image.save(output_path)
    return image

# 打開文件選擇器


class UI:
    SETTINGS_FILE = "settings.json"  # 保存用戶設置的文

    def __init__(self, root):
        self.root = root
        self.root.title("文本檢測和識别工具")
        self.root.geometry("800x600")      
        self.style = Style(theme='darkly')
        self.current_theme = self.load_theme()
        self.apply_theme(self.current_theme)
        
      
        # 文件選擇按钮
        self.select_frame = ttk.Frame(root)
        self.select_frame.pack(fill="x", padx=10, pady=5)
        self.select_button = tk.Button(self.select_frame, text="選擇圖片文件", command=self.open_file, font=("Arial", 14))
        self.select_button.pack(pady=10)
        
        # 顯示識別結果的文本框
        self.output = ttk.Frame(root)
        self.output.pack(fill="x", padx=10, pady=5)
        self.output_text = tk.Text(self.output, wrap="word", font=("Arial", 12), height=10)
        self.output_text.pack(pady=10, fill="both", expand=True)
        
        # 顯示識別結果的圖片標籤
        self.result = ttk.Frame(root)
        self.result.pack(fill="x", padx=10, pady=5)
        self.result_label = tk.Label(self.result )
        self.result_label.pack(pady=10)        

        # 菜單欄
        self.create_menu()

    def create_menu(self):
        """建立功能表單"""
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # 設置子菜單 - 視窗
        settings_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Settings", menu=settings_menu)

        # 設置 - 字型大小
        settings_menu.add_command(label="Set Font Size", command=self.set_font_size)

        # 設置 - 背景顏色
        settings_menu.add_command(label="Set Background Color", command=self.set_background_color)
        # 設置 - 主題製作器
        settings_menu.add_command(label="Open Theme Creator", command=self.open_theme_creator)
        # 設置主題
        settings_menu.add_command(label="Change Theme", command=self.change_theme)

        # 幫助菜單
        help_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "ORC_model v1.0"))        
        
    # 功能函數
    # File menu functions
    def load_theme(self):
        """重設置文件中加載主题"""
        if os.path.exists(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE, "r") as f:
                settings = json.load(f)
                return settings.get("theme", "darkly")  # 如果未設置主题，返回默認主题
        return "darkly"

    def save_theme(self, theme):
        """保存主题到設置文件"""
        settings = {"theme": theme}
        with open(self.SETTINGS_FILE, "w") as f:
            json.dump(settings, f)

    def change_theme(self):
        """打開更改主题的窗口"""
        theme_window = Toplevel(self.root)
        theme_window.title("Change Theme")
        theme_window.geometry("300x200")        

        # 獲取所有可用主题
        all_themes = self.style.theme_names()
        self.selected_theme = StringVar(value=self.current_theme)

        ttk.Label(theme_window, text="Select Theme:", style="TLabel").pack(pady=10)
        theme_dropdown = ttk.Combobox(
            theme_window, values=all_themes, textvariable=self.selected_theme, state="readonly", style="TCombobox"
        )
        theme_dropdown.pack(pady=10)        

        def apply():
            """應用選定的主题"""
            new_theme = self.selected_theme.get()
            self.apply_theme(new_theme)
            self.current_theme = new_theme
            self.save_theme(new_theme)
            messagebox.showinfo("Theme Changed", f"Theme changed to '{new_theme}'.")
            theme_window.destroy()

        def cancel():
            """取消主题更改"""
            theme_window.destroy()

        # 按鈕區
        button_frame = ttk.Frame(theme_window)
        button_frame.pack(pady=20)
    
        ttk.Button(button_frame, text="Apply", command=apply, style="TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel, style="TButton").pack(side="right", padx=5)

    def apply_theme(self, theme_name):
        """應用主题，如果無效則使用默認主题"""
        try:
            available_themes = self.style.theme_names()
            if theme_name not in available_themes:
                messagebox.showwarning(
                    "Invalid Theme",
                    f"The theme '{theme_name}' is not available. Falling back to default theme.",
                )
                theme_name = "darkly"  # 回退到默認主题                
            self.style.theme_use(theme_name)
            # 强制更新界面
            self.root.update_idletasks()
        except Exception as e:
            messagebox.showerror("Error", f"{e}")


    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", content)

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.text_area.get("1.0", tk.END).strip())

    def exit_app(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()

    def open_theme_creator(self):

        """在控制台執行 python -m ttkcreator"""
        try:
            # 執行命令
            result = subprocess.run(
                ["python", "-m", "ttkcreator"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            # 輸出結果到控制台
            print("Output:")
            print(result.stdout)
            print("Errors (if any):")
            print(result.stderr)
        except Exception as e:
            print(f"Error executing command: {e}")
            
    def set_font_size(self):
        """改變字型大小"""
        size = simpledialog.askinteger("Font Size", "Enter font size (e.g., 10, 12, 16):", minvalue=8, maxvalue=72)
        if size:
            self.update_global_font(size) # 改變全局字型大小
            self.log_message(f"Font size set to {size}.")

    def update_global_font(self, font_size):
        """更新全局字型大小"""
        font_settings = (f"Helvetica {font_size}")
        self.style.configure('.', font=font_settings)  # 更新 ttk 元件樣式
        self.root.option_add("*Font", font_settings)  # 更新 tkinter 元件樣式

        # 更新視窗大小
        self.root.update_idletasks()  # 刷新元件尺寸
        width = max(self.root.winfo_reqwidth(), 800)  # 最小寬度為 800
        height = max(self.root.winfo_reqheight(), 600)  # 最小高度為 600
        self.root.geometry(f"{width}x{height}")  # 調整視窗大小

    def set_background_color(self):
        """改變背景顏色"""
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            self.root.config(bg=color)
            self.log_message(f"Background color set to {color}.")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="選擇圖片文件",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        if not file_path:
            return

        # 使用多線程執行耗時操作
        threading.Thread(target=self.process_image, args=(file_path,), daemon=True).start()

    def process_image(self, file_path):
        """在另一個線程中處理圖像"""
    
        try:
            # 檢測和識别文本
            results = detect_and_recognize_text(file_path)
    
            # 輸出識别结果
            self.output_text.delete("1.0", tk.END)
            if results:
                self.output_text.insert(tk.END, "檢測到的文本：\n")
                for i, (bbox, text, prob) in enumerate(results):
                    self.output_text.insert(tk.END, f"文本框 {i + 1}: '{text}', 置信度: {prob:.2f}\n")
            else:
                self.output_text.insert(tk.END, "未檢測到文本。\n")
    
            # 可視化結果
            result_image = visualize_results(file_path, results)
            
            # 在 GUI 中顯示結果圖片
            result_image_tk = ImageTk.PhotoImage(result_image.resize((400, 300)))
            self.result_label.config(image=result_image_tk)
            self.result_label.image = result_image_tk

        except Exception as e:
            messagebox.showerror("錯誤", f"分析失敗：{e}")

if __name__ == "__main__":
    SETTINGS_FILE = "settings.json"  # 保存用戶設置的文件
    # 創建 Tkinter 窗口
    root = tk.Tk()
    show = UI(root)
    
    # 運行主循環
    root.mainloop()

