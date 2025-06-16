import tkinter as tk
from tkinter import messagebox
import random
import json
import os


class Arkanoid:
    def __init__(self, master):
        self.master = master
        self.master.title("Arkanoid")
        
        # Настройки для сохранения результатов
        self.results_file = "arkanoid_results.json"
        self.results = []
        self.load_results()

        # Создаем контейнер для фреймов
        self.container = tk.Frame(master)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Создаем фреймы для разных экранов
        self.menu_frame = tk.Frame(self.container)
        self.game_frame = tk.Frame(self.container)
        self.results_frame = tk.Frame(self.container)

        for frame in (self.menu_frame, self.game_frame, self.results_frame):
            frame.grid(row=0, column=0, sticky="nsew")

        # Показываем меню при старте
        self.show_menu()

    def show_menu(self):
        self.menu_frame.tkraise()
        
        # Очищаем предыдущие виджеты в меню
        for widget in self.menu_frame.winfo_children():
            widget.destroy()
        
        # Создаем элементы меню
        tk.Label(self.menu_frame, text="Арканоид", font=("Arial", 24)).pack(pady=40)
        
        btn_frame = tk.Frame(self.menu_frame)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Начать игру", command=self.start_game, width=20, height=2).pack(pady=10)
        tk.Button(btn_frame, text="Результаты", command=self.show_results, width=20, height=2).pack(pady=10)
        tk.Button(btn_frame, text="Выход", command=self.master.quit, width=20, height=2).pack(pady=10)

    def show_results(self):
        self.results_frame.tkraise()
        
        # Очищаем предыдущие виджеты
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Заголовок
        tk.Label(self.results_frame, text="Лучшие результаты", font=("Arial", 20)).pack(pady=20)
        
        # Сортировка результатов по убыванию
        sorted_results = sorted(self.results, key=lambda x: x["score"], reverse=True)
        
        # Отображаем топ-10 результатов
        results_text = tk.Text(self.results_frame, width=40, height=15, font=("Arial", 12))
        results_text.pack(pady=10)
        
        if not sorted_results:
            results_text.insert(tk.END, "Пока нет результатов")
        else:
            for i, result in enumerate(sorted_results[:10], 1):
                results_text.insert(tk.END, f"{i}. {result['name']}: {result['score']}\n")
        
        results_text.config(state=tk.DISABLED)
        
        # Кнопка возврата в меню
        tk.Button(self.results_frame, text="В меню", command=self.show_menu).pack(pady=20)

    def start_game(self):
        self.game_frame.tkraise()
        
        # Очищаем предыдущие виджеты
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        
        # Настройки игрового поля
        self.canvas_width = 600
        self.canvas_height = 600
        self.canvas = tk.Canvas(self.game_frame, width=self.canvas_width, height=self.canvas_height, bg="black")
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
        self.master.bind("<Escape>", self.return_to_menu)  # Добавили выход в меню по Esc

        # Игровые параметры
        self.game_active = False
        self.game_paused = False
        self.lives = 3
        self.score = 0
        self.player_name = "Player"  # Имя игрока по умолчанию

        # Отображение жизней и счета
        self.label_lives = self.canvas.create_text(
            50, 20,
            text=f"Lives: {self.lives}",
            fill="white", font=("Arial", 12),
            anchor="w"
        )

        self.label_score = self.canvas.create_text(
            self.canvas_width - 50, 20,
            text=f"Score: {self.score}",
            fill="white", font=("Arial", 12),
            anchor="e"
        )

        # Начальное сообщение
        self.start_text = self.canvas.create_text(
            self.canvas_width / 2, self.canvas_height / 2,
            text="Press SPACE to start",
            fill="white", font=("Arial", 20)
        )

        # Текст паузы
        self.pause_text = None

    def return_to_menu(self, event=None):
        if not self.game_active or messagebox.askyesno("Выход", "Вы уверены, что хотите выйти в меню?"):
            self.show_menu()

    def toggle_pause(self, event):
        if not self.game_active and not self.game_paused:
            self.start_game_loop()
        elif self.game_active:
            self.game_active = False
            self.game_paused = True
            self.pause_text = self.canvas.create_text(
                self.canvas_width / 2, self.canvas_height / 2,
                text="PAUSED\nPress SPACE or P to continue",
                fill="white", font=("Arial", 20),
                justify="center"
            )
        elif self.game_paused:
            self.game_active = True
            self.game_paused = False
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
                    'id': self.canvas.create_rectangle(x, y, x + self.block_width, y + self.block_height,
                                                       fill=color),
                    'x': x, 'y': y,
                    'width': self.block_width, 'height': self.block_height,
                    'color': color
                }
                self.blocks.append(block)

    def move_paddle_left(self, event):
        if self.game_active:
            self.paddle_x = max(0, self.paddle_x - 30)
            self.canvas.coords(self.paddle,
                               self.paddle_x, self.paddle_y,
                               self.paddle_x + self.paddle_width, self.paddle_y + self.paddle_height)

    def move_paddle_right(self, event):
        if self.game_active:
            self.paddle_x = min(self.canvas_width - self.paddle_width, self.paddle_x + 30)
            self.canvas.coords(self.paddle,
                               self.paddle_x, self.paddle_y,
                               self.paddle_x + self.paddle_width, self.paddle_y + self.paddle_height)

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

        self.canvas.coords(self.ball,
                           self.ball_x - self.ball_size, self.ball_y - self.ball_size,
                           self.ball_x + self.ball_size, self.ball_y + self.ball_size)

    def check_collisions(self):
        # Коллизия с платформой
        paddle_coords = self.canvas.coords(self.paddle)
        if (self.ball_y + self.ball_size >= paddle_coords[1] and
                self.ball_y - self.ball_size <= paddle_coords[3] and
                self.ball_x + self.ball_size >= paddle_coords[0] and
                self.ball_x - self.ball_size <= paddle_coords[2]):
            self.ball_y_speed *= -1

        # Коллизия с блоками
        for block in self.blocks[:]:
            block_left = block['x']
            block_right = block['x'] + block['width']
            block_top = block['y']
            block_bottom = block['y'] + block['height']

            ball_left = self.ball_x - self.ball_size
            ball_right = self.ball_x + self.ball_size
            ball_top = self.ball_y - self.ball_size
            ball_bottom = self.ball_y + self.ball_size

            if (ball_right > block_left and
                    ball_left < block_right and
                    ball_bottom > block_top and
                    ball_top < block_bottom):

                # Удаляем блок
                self.canvas.delete(block['id'])
                self.blocks.remove(block)
                self.score += 10
                self.canvas.itemconfig(self.label_score, text=f"Score: {self.score}")

                # Определяем направление отскока
                delta_left = abs(ball_right - block_left)
                delta_right = abs(ball_left - block_right)
                delta_top = abs(ball_bottom - block_top)
                delta_bottom = abs(ball_top - block_bottom)

                min_delta = min(delta_left, delta_right, delta_top, delta_bottom)

                if min_delta == delta_left or min_delta == delta_right:
                    self.ball_x_speed *= -1
                else:
                    self.ball_y_speed *= -1

                break

        # Проверка выхода за нижнюю границу
        if self.ball_y + self.ball_size > self.canvas_height:
            self.lives -= 1
            self.canvas.itemconfig(self.label_lives, text=f"Lives: {self.lives}")
            if self.lives > 0:
                self.reset_ball()
            else:
                self.game_over()

    def reset_ball(self):
        self.ball_x = self.canvas_width / 2
        self.ball_y = self.canvas_height / 2
        self.ball_x_speed = 3 * (1 if random.random() > 0.5 else -1)
        self.ball_y_speed = -3
        self.game_active = False
        self.game_paused = False
        self.start_text = self.canvas.create_text(
            self.canvas_width / 2, self.canvas_height / 2,
            text="Press SPACE to continue",
            fill="white", font=("Arial", 20))

    def game_over(self):
        self.game_active = False
        self.game_paused = False
        self.canvas.create_text(
            self.canvas_width / 2, self.canvas_height / 2 - 30,
            text="Game Over!", fill="red", font=("Arial", 30))
        
        self.save_result()
        
        # Кнопка возврата в меню
        self.menu_btn = tk.Button(self.game_frame, text="В меню", command=self.show_menu)
        self.menu_btn_window = self.canvas.create_window(
            self.canvas_width / 2, self.canvas_height / 2 + 30,
            window=self.menu_btn
        )

    def level_completed(self):
        self.game_active = False
        self.game_paused = False
        self.canvas.create_text(
            self.canvas_width / 2, self.canvas_height / 2 - 30,
            text="Level Completed!", fill="green", font=("Arial", 30))
        
        self.save_result()
        
        # Кнопка возврата в меню
        self.menu_btn = tk.Button(self.game_frame, text="В меню", command=self.show_menu)
        self.menu_btn_window = self.canvas.create_window(
            self.canvas_width / 2, self.canvas_height / 2 + 30,
            window=self.menu_btn
        )

    def save_result(self):
        # Запрашиваем имя игрока
        self.player_name = simpledialog.askstring("Результат", "Введите ваше имя:", parent=self.master)
        if not self.player_name:
            self.player_name = "Player"
            
        # Сохраняем результат
        self.results.append({
            "name": self.player_name,
            "score": self.score,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Сохраняем в файл
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


# Импорты для работы с датой и диалоговыми окнами
from datetime import datetime
from tkinter import simpledialog


if __name__ == "__main__":
    root = tk.Tk()
    game = Arkanoid(root)
    root.mainloop()
