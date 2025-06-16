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
        
        # Скрываем курсор мыши (изначально видим)
        self.cursor_visible = True
        self.master.config(cursor="")

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

    def toggle_cursor(self, visible):
        """Переключает видимость курсора мыши"""
        if visible:
            self.master.config(cursor="")
            self.cursor_visible = True
        else:
            self.master.config(cursor="none")
            self.cursor_visible = False

    def show_menu(self):
        self.menu_frame.tkraise()
        self.toggle_cursor(True)  # Показываем курсор в меню
        
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
        
        # Ярко-зелёный цвет для текста
        text_color = "#00FF00"
        
        # Заголовок игры
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
            "bg": "#111",
            "fg": text_color,
            "activebackground": "#333",
            "activeforeground": text_color,
            "bd": 0,
            "highlightthickness": 0,
            "highlightbackground": text_color,
            "highlightcolor": text_color
        }
        
        # Создаем кнопки
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
        
        # Декоративные линии
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

    def start_game(self):
        self.game_frame.tkraise()
        self.toggle_cursor(False)  # Скрываем курсор в игре
        
        # Очищаем предыдущие виджеты
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        
        # Создаем игровое поле
        self.canvas = tk.Canvas(
            self.game_frame, 
            width=self.canvas_width, 
            height=self.canvas_height, 
            bg="black", 
            highlightthickness=0
        )
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

        # Управление мышью
        self.canvas.bind("<Motion>", self.move_paddle_mouse)
        
        # Управление клавишами
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
            fill="white", 
            font=("Arial", 12),
            anchor="w"
        )

        self.label_score = self.canvas.create_text(
            self.canvas_width - 50, 20,
            text=f"Очки: {self.score}",
            fill="white", 
            font=("Arial", 12),
            anchor="e"
        )

        # Начальное сообщение
        self.start_text = self.canvas.create_text(
            self.canvas_width / 2, self.canvas_height / 2,
            text="Нажмите ПРОБЕЛ чтобы начать",
            fill="white", 
            font=("Arial", 20)
        )

        # Текст паузы
        self.pause_text = None

    def move_paddle_mouse(self, event):
        """Движение платформы за мышью"""
        if self.game_active and not self.game_paused:
            # Центрируем платформу по курсору мыши
            self.paddle_x = event.x - self.paddle_width / 2
            
            # Ограничиваем движение в пределах поля
            self.paddle_x = max(0, min(self.paddle_x, self.canvas_width - self.paddle_width))
            
            self.canvas.coords(
                self.paddle,
                self.paddle_x, self.paddle_y,
                self.paddle_x + self.paddle_width, self.paddle_y + self.paddle_height
            )

    def return_to_menu(self, event=None):
        self.toggle_cursor(True)  # Показываем курсор при возврате в меню
        if not self.game_active or messagebox.askyesno("Выход", "Вы уверены, что хотите выйти в меню?"):
            self.show_menu()

    def toggle_pause(self, event):
        if not self.game_active and not self.game_paused:
            self.start_game_loop()
        elif self.game_active:
            self.game_active = False
            self.game_paused = True
            self.toggle_cursor(True)  # Показываем курсор на паузе
            self.pause_text = self.canvas.create_text(
                self.canvas_width / 2, self.canvas_height / 2,
                text="ПАУЗА\nНажмите ПРОБЕЛ или P чтобы продолжить",
                fill="white", 
                font=("Arial", 20),
                justify="center"
            )
        elif self.game_paused:
            self.game_active = True
            self.game_paused = False
            self.toggle_cursor(False)  # Снова скрываем курсор
            self.canvas.delete(self.pause_text)
            self.game_loop()

    # ... (остальные методы остаются без изменений, как в предыдущем коде)


if __name__ == "__main__":
    root = tk.Tk()
    game = Arkanoid(root)
    root.mainloop()
