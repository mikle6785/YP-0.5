import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import json
import os
from datetime import datetime


class Arkanoid:
    def __init__(self, master):
        self.master = master
        self.master.title("Arkanoid")
        
        # Настройки для сохранения результатов
        self.results_file = "arkanoid_results.json"
        self.results = []
        self.load_results()

        # Размеры окна
        self.canvas_width = 600
        self.canvas_height = 600
        self.master.geometry(f"{self.canvas_width}x{self.canvas_height}")

        # Создаем контейнер для фреймов
        self.container = tk.Frame(master, bg="black")
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Создаем фреймы для разных экранов
        self.menu_frame = tk.Frame(self.container, bg="black")
        self.game_frame = tk.Frame(self.container, bg="black")
        self.results_frame = tk.Frame(self.container, bg="black")

        for frame in (self.menu_frame, self.game_frame, self.results_frame):
            frame.grid(row=0, column=0, sticky="nsew")

        # Показываем меню при старте
        self.show_menu()

    def show_menu(self):
        self.menu_frame.tkraise()
        
        # Очищаем предыдущие виджеты в меню
        for widget in self.menu_frame.winfo_children():
            widget.destroy()
        
        # Создаем Canvas для меню с чёрным фоном
        menu_canvas = tk.Canvas(
            self.menu_frame, 
            width=self.canvas_width, 
            height=self.canvas_height, 
            bg="black", 
            highlightthickness=0
        )
        menu_canvas.pack(fill="both", expand=True)
        
        # Ярко-зелёный цвет для текста (#00FF00 или #32CD32)
        text_color = "#00FF00"
        
        # Заголовок игры (ярко-зелёный)
        menu_canvas.create_text(
            self.canvas_width/2, 150,
            text="АРКАНОИД",
            fill=text_color, 
            font=("Arial", 36, "bold"),
            anchor="center"
        )
        
        # Стиль для кнопок
        button_style = {
            "font": ("Arial", 16),
            "width": 20,
            "height": 2,
            "bg": "#111",  # Тёмный фон кнопок
            "fg": text_color,  # Ярко-зелёный текст
            "activebackground": "#333",
            "activeforeground": text_color,
            "bd": 0,
            "highlightthickness": 0,
            "highlightbackground": text_color,
            "highlightcolor": text_color
        }
        
        # Создаем кнопки с зелёным текстом
        btn_start = tk.Button(
            menu_canvas, 
            text="НАЧАТЬ ИГРУ", 
            command=self.start_game, 
            **button_style
        )
        btn_results = tk.Button(
            menu_canvas, 
            text="РЕЗУЛЬТАТЫ", 
            command=self.show_results, 
            **button_style
        )
        btn_exit = tk.Button(
            menu_canvas, 
            text="ВЫХОД", 
            command=self.master.quit, 
            **button_style
        )
        
        # Размещаем кнопки по центру
        menu_canvas.create_window(self.canvas_width/2, 300, window=btn_start, anchor="center")
        menu_canvas.create_window(self.canvas_width/2, 370, window=btn_results, anchor="center")
        menu_canvas.create_window(self.canvas_width/2, 440, window=btn_exit, anchor="center")
        
        # Декоративные элементы (ярко-зелёные линии)
        menu_canvas.create_line(
            100, 200, 
            self.canvas_width-100, 200, 
            fill=text_color, 
            width=2
        )
        menu_canvas.create_line(
            100, 500, 
            self.canvas_width-100, 500, 
            fill=text_color, 
            width=2
        )

    # ... (остальные методы класса остаются без изменений)


if __name__ == "__main__":
    root = tk.Tk()
    game = Arkanoid(root)
    root.mainloop()
