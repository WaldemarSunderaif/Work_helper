# Main.py

import hashlib
import sys
import flet as ft
import json
import os
from dotenv import load_dotenv
from Chance import start_chance, check_detect, stop_browser
import tempfile
import shutil
import threading  # Добавляем модуль threading

# Распаковываем .env файл из ресурсов PyInstaller во временную папку
def extract_env():
    tmpdir = tempfile.gettempdir()
    env_path = os.path.join(tmpdir, '.env')
    if not os.path.exists(env_path):
        shutil.copyfile(os.path.join(sys._MEIPASS, '.env'), env_path)
    load_dotenv(env_path)
extract_env()

load_dotenv()

# Путь к файлу для сохранения данных
DATA_FILE = "data.json"

# Глобальная переменная для режима headless
headless_mode = False  # По умолчанию режим отключен

# Глобальная переменная для потока
chance_thread = None

# Хеширование пароля
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Получение паролей из переменных среды
passwords = [
    os.getenv("SECRET_PASSWORD_1"),
    os.getenv("SECRET_PASSWORD_2"),
    os.getenv("SECRET_PASSWORD_3"),
    os.getenv("SECRET_PASSWORD_4"),
    os.getenv("SECRET_PASSWORD_5"),
    os.getenv("SECRET_PASSWORD_6"),
]

# Удаляем None значения из списка паролей перед хешированием
passwords = [password for password in passwords if password is not None]
hashed_passwords = [hash_password(password) for password in passwords]

# Проверка введённого пароля
def check_password(input_password):
    hashed_input = hash_password(input_password)
    return hashed_input in hashed_passwords

# Загрузка сохранённых данных
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Сохранение данных в файл
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)

# Функция для отображения SnackBar
def show_snack_bar(page, message):
    snack_bar = ft.SnackBar(ft.Text(message))
    page.overlay.append(snack_bar)
    snack_bar.open = True
    page.update()

# Основное окно
def open_new_window(page: ft.Page):
    global headless_mode
    global chance_thread

    page.controls.clear()
    page.title = "Data Entry"

    # Увеличиваем размер окна с анимацией
    page.window.width = 820
    page.window.height = 410
    page.window.animate_resize = 300
    page.update()

    saved_data = load_data()

    # Поля для ввода данных и чекбоксы
    login_alpha_date = ft.TextField(
        label="Login alpha date",
        value=saved_data.get("login_alpha_date", ""),
        icon=ft.icons.PERSON,
        width=700)
    save_login_checkbox = ft.Checkbox(label="Save", value=True)

    password_alpha_date = ft.TextField(
        label="Password alpha date",
        value=saved_data.get("password_alpha_date", ""),
        icon=ft.icons.LOCK,
        password=True,
        can_reveal_password=True,
        width=700)
    save_password_checkbox = ft.Checkbox(label="Save", value=True)

    invite1 = ft.TextField(
        label="Invite N1",
        value=saved_data.get("invite1", ""),
        icon=ft.icons.EMAIL,
        width=700)
    save_invite1_checkbox = ft.Checkbox(label="Save", value=True)

    invite2 = ft.TextField(
        label="Invite N2",
        value=saved_data.get("invite2", ""),
        icon=ft.icons.EMAIL,
        width=700)
    save_invite2_checkbox = ft.Checkbox(label="Save", value=True)

    # Функция для обработки сохранения данных в зависимости от чекбоксов
    def handle_save_data():
        data_to_save = {}

        if save_login_checkbox.value:
            data_to_save["login_alpha_date"] = login_alpha_date.value

        if save_password_checkbox.value:
            data_to_save["password_alpha_date"] = password_alpha_date.value

        if save_invite1_checkbox.value:
            data_to_save["invite1"] = invite1.value

        if save_invite2_checkbox.value:
            data_to_save["invite2"] = invite2.value

        return data_to_save

    # Функция для очистки всех полей
    def reset_process(e):
        login_alpha_date.value = ""
        password_alpha_date.value = ""
        invite1.value = ""
        invite2.value = ""
        page.update()

    # Функция для очистки всех несохранённых полей
    def clear_unsaved_fields(e):
        if not save_login_checkbox.value:
            login_alpha_date.value = ""
        if not save_password_checkbox.value:
            password_alpha_date.value = ""
        if not save_invite1_checkbox.value:
            invite1.value = ""
        if not save_invite2_checkbox.value:
            invite2.value = ""
        page.update()

    # Функция для переключения режима headless
    def toggle_headless(e):
        global headless_mode
        headless_mode = not headless_mode
        show_snack_bar(page, f"Headless mode {'enabled' if headless_mode else 'disabled'}")

    # Функция для сохранения данных
    def save_process(e):
        data_to_save = handle_save_data()
        save_data(data_to_save)
        show_snack_bar(page, "Data saved successfully!")

    # Функция для загрузки данных
    def load_process(e):
        loaded_data = load_data()
        login_alpha_date.value = loaded_data.get("login_alpha_date", "")
        password_alpha_date.value = loaded_data.get("password_alpha_date", "")
        invite1.value = loaded_data.get("invite1", "")
        invite2.value = loaded_data.get("invite2", "")
        show_snack_bar(page, "Data loaded successfully!")
        page.update()

    # Обработка нажатия на кнопку "Start"
    def start_process(e):
        global chance_thread

        if check_password(password_alpha_date.value):
            data_to_save = handle_save_data()
            save_data(data_to_save)
            try:
                # Запускаем start_chance в отдельном потоке
                chance_thread = threading.Thread(target=start_chance, args=(headless_mode,))
                chance_thread.start()
                show_snack_bar(page, "Process started!")
            except Exception as error:
                show_snack_bar(page, f"Error: {error}")
                print(f"Произошла ошибка при запуске: {error}")
        else:
            show_snack_bar(page, "Invalid password!")
        page.update()

    # Обработка нажатия на кнопку "Check"
    def check_process(e):
        check_detect()
        show_snack_bar(page, "Bot check complete!")

    # Функция для полной остановки всех процессов
    def stop_process(e):
        global chance_thread

        stop_browser()  # Вызов функции остановки браузера

        # Ждем завершения потока
        if chance_thread and chance_thread.is_alive():
            chance_thread.join()
            chance_thread = None

        show_snack_bar(page, "Processes stopped.")

    # Кнопки управления
    check_button = ft.ElevatedButton(text="Check", on_click=check_process, bgcolor=ft.colors.YELLOW, color=ft.colors.BLACK)
    start_button = ft.ElevatedButton(text="Start", on_click=start_process, bgcolor=ft.colors.GREEN, color=ft.colors.BLACK)
    stop_button = ft.ElevatedButton(text="Stop", on_click=stop_process, bgcolor=ft.colors.RED, color=ft.colors.BLACK)
    save_button = ft.ElevatedButton(text="Save", on_click=save_process, bgcolor=ft.colors.BLUE, color=ft.colors.WHITE)
    load_button = ft.ElevatedButton(text="Load", on_click=load_process, bgcolor=ft.colors.PURPLE, color=ft.colors.WHITE)
    reset_button = ft.ElevatedButton(text="Reset", on_click=reset_process, bgcolor=ft.colors.ORANGE, color=ft.colors.BLACK)
    clear_button = ft.ElevatedButton(
        text="Clear",
        on_click=clear_unsaved_fields,
        icon=ft.icons.DELETE,
        bgcolor=ft.colors.GREY,
        color=ft.colors.BLACK,
    )
    toggle_headless_button = ft.ElevatedButton(
        text="Toggle Headless",
        on_click=toggle_headless,
        bgcolor=ft.colors.BROWN,
        color=ft.colors.WHITE,
    )

    # Размещение кнопок в два ряда
    button_row1 = ft.Row(
        [check_button, start_button, stop_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )
    button_row2 = ft.Row(
        [save_button, load_button, reset_button, clear_button, toggle_headless_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    # Контейнер для кнопок
    buttons_container = ft.Container(
        content=ft.Column([button_row1, button_row2], spacing=10),
        alignment=ft.alignment.center
    )

    # Размещение полей с чекбоксами и кнопок на странице
    page.add(
        ft.Column(
            [
                ft.Row([login_alpha_date, save_login_checkbox], spacing=10),
                ft.Row([password_alpha_date, save_password_checkbox], spacing=10),
                ft.Row([invite1, save_invite1_checkbox], spacing=10),
                ft.Row([invite2, save_invite2_checkbox], spacing=10),
                buttons_container
            ],
            spacing=20
        )
    )
    page.update()

    # Обработчик закрытия окна
    def on_close(e):
        stop_process(None)
        page.window.close()

    page.on_window_close = on_close  # Назначаем обработчик события закрытия окна

# Окно логина
def main(page: ft.Page):
    page.title = "Login"
    page.window_width = 300
    page.window_height = 400
    page.window_center()

    password_field = ft.TextField(label="Enter Password", password=True)
    login_button = ft.ElevatedButton(
        text="Login",
        on_click=lambda e: open_new_window(page) if check_password(password_field.value) else page.window.close()
    )

    page.add(
        ft.Container(
            content=ft.Column(
                [ft.Text("Login", size=34, weight=ft.FontWeight.BOLD), password_field, login_button],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            width=400,
            height=300,
            padding=10,
            border_radius=ft.border_radius.all(10),
            bgcolor=ft.colors.BLACK12,
            alignment=ft.alignment.center
        )
    )

# Запуск приложения
ft.app(target=main)
