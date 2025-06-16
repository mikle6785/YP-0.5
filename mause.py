import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import json
import os
import time
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
        
        # Настройки курсора
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
        self.toggle_cursor(True)
        
        # Очищаем предыдущие виджеты в меню
        for widget in self.menu_frame.winfo_children():
            widget.destroy()
        
        # Создаем Canvas для меню
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
        
        # Размещаем кнопки
        menu_canvas.create_window(self.canvas_width/2, 300, window=btn_start, anchor="center")
        menu_canvas.create_window(self.canvas_width/2, 370, window=btn_results, anchor="center")
        menu_canvas.create_window(self.canvas_width/2, 440, window=btn_exit, anchor="center")
        
        # Декоративные линии
        menu_canvas.create_line(100, 200, self.canvas_width-100, 200, fill=text_color, width=2)
        menu_canvas.create_line(100, 500, self.canvas_width-100, 500, fill=text_color, width=2)

    def show_results(self):
        self.results_frame.tkraise()
        self.toggle_cursor(True)
        
        # Очищаем предыдущие виджеты
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Создаем canvas для результатов
        results_canvas = tk.Canvas(
            self.results_frame, 
            width=self.canvas_width, 
            height=self.canvas_height, 
            bg="black", 
            highlightthickness=0
        )
        results_canvas.pack(fill="both", expand=True)
        
        text_color = "#00FF00"
        
        # Заголовок
        results_canvas.create_text(
            self.canvas_width/2, 50,
            text="ЛУЧШИЕ РЕЗУЛЬТАТЫ",
            fill=text_color, 
            font=("Arial", 24, "bold"),
            anchor="center"
        )
        
        # Сортировка результатов
        sorted_results = sorted(self.results, key=lambda x: x["score"], reverse=True)
        
        # Отображаем топ-10
        y_position = 100
        if not sorted_results:
            results_canvas.create_text(
                self.canvas_width/2, y_position,
                text="Пока нет результатов",
                fill=text_color, 
                font=("Arial", 16),
                anchor="center"
            )
        else:
            for i, result in enumerate(sorted_results[:10], 1):
                results_canvas.create_text(
                    150, y_position,
                    text=f"{i}. {result['name']}",
                    fill=text_color, 
                    font=("Arial", 14),
                    anchor="w"
                )
                results_canvas.create_text(
                    self.canvas_width-150, y_position,
                    text=f"{result['score']}",
                    fill=text_color, 
                    font=("Arial", 14),
                    anchor="e"
                )
                y_position += 40
        
        # Кнопка возврата
        btn_style = {
            "font": ("Arial", 14),
            "width": 15,
            "height": 1,
            "bg": "#111",
            "fg": text_color,
            "activebackground": "#333",
            "bd": 0
        }
        btn_back = tk.Button(
            results_canvas, 
            text="В МЕНЮ", 
            command=self.show_menu, 
            **btn_style
        )
        results_canvas.create_window(
            self.canvas_width/2, 
            self.canvas_height-50, 
            window=btn_back, 
            anchor="center"
        )

    def start_game(self):
        self.game_frame.tkraise()
        self.toggle_cursor(False)
        
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
        self.ball_x_speed = 3 * (1 if random.random() > 0.5 else -1)
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
        self.last_paddle_collision_time = 0  # Для предотвращения залипания

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
            self.paddle_x = max(0, min(event.x - self.paddle_width/2, self.canvas_width - self.paddle_width))
            self.canvas.coords(
                self.paddle,
                self.paddle_x, self.paddle_y,
                self.paddle_x + self.paddle_width, self.paddle_y + self.paddle_height
            )

    def return_to_menu(self, event=None):
        self.toggle_cursor(True)
        if not self.game_active or messagebox.askyesno("Выход", "Вы уверены, что хотите выйти в меню?"):
            self.show_menu()

    def toggle_pause(self, event):
        if not self.game_active and not self.game_paused:
            self.start_game_loop()
        elif self.game_active:
            self.game_active = False
            self.game_paused = True
            self.toggle_cursor(True)
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
            self.toggle_cursor(False)
            self.canvas.delete(self.pause_text)
            self.game_loop()

    def start_game_loop(self):
        if not self.game_active and not self.game_paused:
            self.game_active = True
            self.canvas.delete(self.start_text)
            self.game_loop()

    def create_blocks(self):
        colors = ["red", "orange", "yellow", "green", "blue", "purple"]
        rows = 5
        cols = 10
        for row in range(rows):
            for col in range(cols):
                x = col * (self.block_width + 5) + 40
                y = row * (self.block_height + 5) + 60
                color = random.choice(colors)
                block = {
                    'id': self.canvas.create_rectangle(x, y, x + self.block_width, y + self.block_height, fill=color),
                    'x': x, 'y': y,
                    'width': self.block_width, 'height': self.block_height,
                    'color': color
                }
                self.blocks.append(block)

    def game_loop(self):
        if not self.game_active or self.game_paused:
            return

        self.move_ball()
        self.check_collisions()

        if self.lives <= 0:
            self.game_over()
            return

        if not self.blocks:
            self.level_completed()
            return

        self.master.after(30, self.game_loop)

    def move_ball(self):
        if self.game_paused:
            return

        self.ball_x += self.ball_x_speed
        self.ball_y += self.ball_y_speed

        # Отражение от стен
        if self.ball_x - self.ball_size <= 0 or self.ball_x + self.ball_size >= self.canvas_width:
            self.ball_x_speed *= -1
        if self.ball_y - self.ball_size <= 0:
            self.ball_y_speed *= -1

        self.canvas.coords(
            self.ball,
            self.ball_x - self.ball_size, self.ball_y - self.ball_size,
            self.ball_x + self.ball_size, self.ball_y + self.ball_size
        )

    def check_collisions(self):
        current_time = time.time() * 1000  # Текущее время в миллисекундах
        
        # Коллизия с платформой
        paddle_coords = self.canvas.coords(self.paddle)
        ball_coords = self.canvas.coords(self.ball)
        
        if (ball_coords[3] >= paddle_coords[1] and 
            ball_coords[1] <= paddle_coords[3] and 
            ball_coords[2] >= paddle_coords[0] and 
            ball_coords[0] <= paddle_coords[2]):
            
            # Проверяем временной интервал с момента последнего столкновения
            if current_time - self.last_paddle_collision_time > 100:  # 100 мс задержки
                # Вычисляем относительное положение удара по платформе
                hit_pos = (self.ball_x - (self.paddle_x + self.paddle_width/2)) / (self.paddle_width/2)
                
                # Меняем направление мяча с учетом места удара
                self.ball_x_speed = hit_pos * 5  # Максимальный угол отскока
                self.ball_y_speed = -abs(self.ball_y_speed)  # Гарантированный отскок вверх
                
                # Ограничиваем максимальную скорость
                max_speed = 5
                speed = (self.ball_x_speed**2 + self.ball_y_speed**2)**0.5
                if speed > max_speed:
                    factor = max_speed / speed
                    self.ball_x_speed *= factor
                    self.ball_y_speed *= factor
                
                self.last_paddle_collision_time = current_time

        # Коллизия с блоками
        for block in self.blocks[:]:
            block_coords = (
                block['x'], block['y'],
                block['x'] + block['width'], block['y'] + block['height']
            )
            
            if self.check_rect_collision(ball_coords, block_coords):
                self.canvas.delete(block['id'])
                self.blocks.remove(block)
                self.score += 10
                self.canvas.itemconfig(self.label_score, text=f"Очки: {self.score}")

                # Определяем направление отскока
                overlap_left = abs(ball_coords[2] - block_coords[0])
                overlap_right = abs(ball_coords[0] - block_coords[2])
                overlap_top = abs(ball_coords[3] - block_coords[1])
                overlap_bottom = abs(ball_coords[1] - block_coords[3])

                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                if min_overlap == overlap_left or min_overlap == overlap_right:
                    self.ball_x_speed *= -1
                else:
                    self.ball_y_speed *= -1

                break

        # Проверка выхода за нижнюю границу
        if self.ball_y + self.ball_size > self.canvas_height:
            self.lives -= 1
            self.canvas.itemconfig(self.label_lives, text=f"Жизни: {self.lives}")
            if self.lives > 0:
                self.reset_ball()
            else:
                self.game_over()

    def check_rect_collision(self, rect1, rect2):
        """Проверка столкновения двух прямоугольников"""
        return not (rect1[2] < rect2[0] or 
                   rect1[0] > rect2[2] or 
                   rect1[3] < rect2[1] or 
                   rect1[1] > rect2[3])

    def reset_ball(self):
        self.ball_x = self.canvas_width / 2
        self.ball_y = self.canvas_height / 2
        self.ball_x_speed = 3 * (1 if random.random() > 0.5 else -1)
        self.ball_y_speed = -3
        self.game_active = False
        self.game_paused = False
        self.toggle_cursor(True)
        self.start_text = self.canvas.create_text(
            self.canvas_width / 2, self.canvas_height / 2,
            text="Нажмите ПРОБЕЛ чтобы продолжить",
            fill="white", 
            font=("Arial", 20)
        )

    def game_over(self):
        self.game_active = False
        self.game_paused = False
        self.toggle_cursor(True)
        self.canvas.create_text(
            self.canvas_width / 2, self.canvas_height / 2 - 30,
            text="ИГРА ОКОНЧЕНА!",
            fill="red", 
            font=("Arial", 30)
        )
        
        self.save_result()
        
        # Кнопка возврата в меню
        btn_style = {
            "font": ("Arial", 14),
            "bg": "#111",
            "fg": "#00FF00",
            "bd": 0
        }
        self.menu_btn = tk.Button(
            self.game_frame, 
            text="В МЕНЮ", 
            command=self.show_menu,
            **btn_style
        )
        self.menu_btn_window = self.canvas.create_window(
            self.canvas_width / 2, self.canvas_height / 2 + 30,
            window=self.menu_btn
        )

    def level_completed(self):
        self.game_active = False
        self.game_paused = False
        self.toggle_cursor(True)
        self.canvas.create_text(
            self.canvas_width / 2, self.canvas_height / 2 - 30,
            text="УРОВЕНЬ ПРОЙДЕН!",
            fill="green", 
            font=("Arial", 30)
        )
        
        self.save_result()
        
        # Кнопка возврата в меню
        btn_style = {
            "font": ("Arial", 14),
            "bg": "#111",
            "fg": "#00FF00",
            "bd": 0
        }
        self.menu_btn = tk.Button(
            self.game_frame, 
            text="В МЕНЮ", 
            command=self.show_menu,
            **btn_style
        )
        self.menu_btn_window = self.canvas.create_window(
            self.canvas_width / 2, self.canvas_height / 2 + 30,
            window=self.menu_btn
        )

    def save_result(self):
        self.player_name = simpledialog.askstring(
            "Результат", 
            "Введите ваше имя:", 
            parent=self.master
        )
        if not self.player_name:
            self.player_name = "Player"
            
        self.results.append({
            "name": self.player_name,
            "score": self.score,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.save_results()

    def load_results(self):
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, "r") as f:
                    self.results = json.load(f)
            except:
                self.results = []
        else:
            self.results = []

    def save_results(self):
        with open(self.results_file, "w") as f:
            json.dump(self.results, f)


if __name__ == "__main__":
    root = tk.Tk()
    game = Arkanoid(root)
    root.mainloop()
    root = tk.Tk()
    game = Arkanoid(root)
    root.mainloop()
