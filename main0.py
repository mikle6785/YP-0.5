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

        # Размеры окна (как в игровом поле)
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
        
        # Создаем элементы меню на черном фоне
        menu_canvas = tk.Canvas(self.menu_frame, width=self.canvas_width, height=self.canvas_height, bg="black", highlightthickness=0)
        menu_canvas.pack(fill="both", expand=True)
        
        # Заголовок игры
        menu_canvas.create_text(
            self.canvas_width/2, 150,
            text="АРКАНОИД",
            fill="white", font=("Arial", 36, "bold"),
            anchor="center"
        )
        
        # Кнопки меню
        button_style = {
            "font": ("Arial", 16),
            "width": 20,
            "height": 2,
            "bg": "#333",
            "fg": "white",
            "activebackground": "#555",
            "activeforeground": "white",
            "bd": 0,
            "highlightthickness": 0
        }
        
        # Создаем кнопки на canvas
        btn_start = tk.Button(menu_canvas, text="НАЧАТЬ ИГРУ", command=self.start_game, **button_style)
        btn_results = tk.Button(menu_canvas, text="РЕЗУЛЬТАТЫ", command=self.show_results, **button_style)
        btn_exit = tk.Button(menu_canvas, text="ВЫХОД", command=self.master.quit, **button_style)
        
        # Размещаем кнопки по центру
        menu_canvas.create_window(self.canvas_width/2, 300, window=btn_start, anchor="center")
        menu_canvas.create_window(self.canvas_width/2, 370, window=btn_results, anchor="center")
        menu_canvas.create_window(self.canvas_width/2, 440, window=btn_exit, anchor="center")
        
        # Декоративные элементы (необязательно)
        menu_canvas.create_line(100, 200, self.canvas_width-100, 200, fill="white", width=2)
        menu_canvas.create_line(100, 500, self.canvas_width-100, 500, fill="white", width=2)

    def show_results(self):
        self.results_frame.tkraise()
        
        # Очищаем предыдущие виджеты
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Создаем canvas для результатов
        results_canvas = tk.Canvas(self.results_frame, width=self.canvas_width, height=self.canvas_height, bg="black", highlightthickness=0)
        results_canvas.pack(fill="both", expand=True)
        
        # Заголовок
        results_canvas.create_text(
            self.canvas_width/2, 50,
            text="ЛУЧШИЕ РЕЗУЛЬТАТЫ",
            fill="white", font=("Arial", 24, "bold"),
            anchor="center"
        )
        
        # Сортировка результатов по убыванию
        sorted_results = sorted(self.results, key=lambda x: x["score"], reverse=True)
        
        # Отображаем топ-10 результатов
        y_position = 100
        if not sorted_results:
            results_canvas.create_text(
                self.canvas_width/2, y_position,
                text="Пока нет результатов",
                fill="white", font=("Arial", 16),
                anchor="center"
            )
        else:
            for i, result in enumerate(sorted_results[:10], 1):
                results_canvas.create_text(
                    150, y_position,
                    text=f"{i}. {result['name']}",
                    fill="white", font=("Arial", 14),
                    anchor="w"
                )
                results_canvas.create_text(
                    self.canvas_width-150, y_position,
                    text=f"{result['score']}",
                    fill="yellow", font=("Arial", 14),
                    anchor="e"
                )
                y_position += 40
        
        # Кнопка возврата в меню
        btn_style = {
            "font": ("Arial", 14),
            "width": 15,
            "height": 1,
            "bg": "#333",
            "fg": "white",
            "activebackground": "#555",
            "bd": 0
        }
        btn_back = tk.Button(results_canvas, text="В МЕНЮ", command=self.show_menu, **btn_style)
        results_canvas.create_window(self.canvas_width/2, self.canvas_height-50, window=btn_back, anchor="center")

    def start_game(self):
        self.game_frame.tkraise()
        
        # Очищаем предыдущие виджеты
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        
        # Создаем игровое поле
        self.canvas = tk.Canvas(self.game_frame, width=self.canvas_width, height=self.canvas_height, bg="black", highlightthickness=0)
        self.canvas.pack()

        # Параметры платформы
        self.paddle_width = 80
        self.paddle_height = 10
        self.paddle_x = (self.canvas_width - self.paddle_width) / 2
        self.paddle_y = self.canvas_height - self.paddle_height - 20
        self.paddle = self.canvas.create_rectangle(
            self.paddle_x, self.paddle_y,
            self.paddle_x + self.paddle_width, self.paddle_y + self.paddle_height,
            fill="white"
        )

        # Параметры мяча
        self.ball_size = 10
        self.ball_x = self.canvas_width / 2
        self.ball_y = self.canvas_height / 2
        self.ball_x_speed = 3
        self.ball_y_speed = -3
        self.ball = self.canvas.create_oval(
            self.ball_x - self.ball_size, self.ball_y - self.ball_size,
            self.ball_x + self.ball_size, self.ball_y + self.ball_size,
            fill="white"
        )

        # Создание блоков
        self.blocks = []
        self.block_width = 40
        self.block_height = 20
        self.create_blocks()

        # Управление
        self.master.bind("<Left>", self.move_paddle_left)
        self.master.bind("<Right>", self.move_paddle_right)
        self.master.bind("<space>", self.toggle_pause)
        self.master.bind("<p>", self.toggle_pause)
        self.master.bind("<Escape>", self.return_to_menu)

        # Игровые параметры
        self.game_active = False
        self.game_paused = False
        self.lives = 3
        self.score = 0
        self.player_name = "Player"

        # Отображение жизней и счета
        self.label_lives = self.canvas.create_text(
            50, 20,
            text=f"Жизни: {self.lives}",
            fill="white", font=("Arial", 12),
            anchor="w"
        )

        self.label_score = self.canvas.create_text(
            self.canvas_width - 50, 20,
            text=f"Очки: {self.score}",
            fill="white", font=("Arial", 12),
            anchor="e"
        )

        # Начальное сообщение
        self.start_text = self.canvas.create_text(
            self.canvas_width / 2, self.canvas_height / 2,
            text="Нажмите ПРОБЕЛ чтобы начать",
            fill="white", font=("Arial", 20)
        )

        # Текст паузы
        self.pause_text = None

    # ... (остальные методы класса остаются без изменений, как в предыдущем примере)


if __name__ == "__main__":
    root = tk.Tk()
    game = Arkanoid(root)
    root.mainloop()
