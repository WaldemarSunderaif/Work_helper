# Chance.py

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
import time
import json
import os
import re
import threading  # Добавляем модуль threading

# Путь к файлу data.json
DATA_FILE = "data.json"
browser_instance = None  # Инициализируем переменную глобально
stop_event = threading.Event()  # Добавляем глобальную переменную stop_event

# Функция для чтения данных из data.json
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Функция для старта браузера и выполнения логики
def start_chance(headless=True):  # Добавляем параметр headless
    global browser_instance  # Используем глобальную переменную
    global stop_event  # Используем глобальное событие остановки

    # Перед запуском очищаем событие остановки
    stop_event.clear()

    # Чтение данных из файла
    data = load_data()
    login_alpha_date = data.get("login_alpha_date")
    password_alpha_date = data.get("password_alpha_date")
    invite1 = data.get("invite1")
    invite2 = data.get("invite2")

    if not invite1 or not invite2:
        print("Инвайты не найдены в файле data.json!")
        return

    # Настройки браузера
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--no-sandbox")

    # Передаем значение headless
    if headless:
        chrome_options.add_argument("--headless")  # Включаем headless режим
        chrome_options.add_argument("--disable-gpu")  # Отключаем GPU для headless режима

    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    )

    # Указываем правильную версию Chrome
    browser_instance = uc.Chrome(options=chrome_options, version_main=130)

    try:
        # Авторизация на сайте
        browser_instance.get("https://alpha.date/")
        time.sleep(1)
        browser_instance.execute_script("document.body.style.zoom='67%'")  # Устанавливаем зум страницы на 67%
        WebDriverWait(browser_instance, 20).until(EC.presence_of_element_located((By.NAME, 'login'))).send_keys(login_alpha_date)
        password_input = browser_instance.find_element(By.NAME, 'password')
        password_input.clear()
        password_input.send_keys(password_alpha_date + Keys.ENTER)
        time.sleep(5)  # Увеличенная задержка на авторизацию

        # Проверяем, прошел ли логин, ожидая появление кнопки профиля
        try:
            profile_button = WebDriverWait(browser_instance, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-testid='profiles-btn']"))
            )
            print('Логин успешен, найден профиль.')
        except TimeoutException:
            print('Не удалось войти на сайт. Страница профилей не загрузилась.')
            browser_instance.quit()
            return

        # Обработка профилей
        handle_profiles(browser_instance, invite1, invite2)

    finally:
        if browser_instance:
            browser_instance.quit()
            browser_instance = None

# Функция для обработки профилей
def handle_profiles(driver, invite1, invite2):
    profile_index = 0  # Индекс профиля
    while not stop_event.is_set():
        try:
            # Проверка состояния stop_event
            if stop_event.is_set():
                print("Остановка обработки профилей по запросу.")
                break

            # Нажимаем на кнопку профилей
            profile_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='profiles-btn']"))
            )
            profile_button.click()
            print("Открыто меню профилей.")
            time.sleep(5)  # Задержка 5 секунд

            # Проверка состояния stop_event
            if stop_event.is_set():
                print("Остановка обработки профилей по запросу.")
                break

            # Проверяем количество оффлайн профилей
            try:
                offline_text_element = driver.find_element(By.XPATH, "//div[contains(@class, 'styles_clmn_1_mm_chat_offline_girls_text__HqIMp')]")
                offline_text = offline_text_element.text
                match = re.search(r'\d+', offline_text)
                if match:
                    offline_count = int(match.group())
                else:
                    offline_count = 0
                print(f"Найдено {offline_count} оффлайн профилей.")
            except NoSuchElementException:
                print("Информация о количестве оффлайн профилей не найдена.")
                offline_count = 0

            if offline_count > 0:
                try:
                    # Ищем кнопку активации профилей и кликаем
                    activate_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='activate-all-profiles']"))
                    )
                    activate_button.click()
                    print(f"Профили активированы.")
                    time.sleep(5)  # Ожидаем активации
                except NoSuchElementException:
                    print("Кнопка активации профилей не найдена.")
            else:
                print("Все профили онлайн.")

            # Кликаем на текущий профиль
            profiles = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'styles_clmn_1_mm_chat_list_item__YtyB6')]"))
            )
            total_profiles = len(profiles)
            print(f"Найдено {total_profiles} профилей.")

            if profile_index >= total_profiles:
                profile_index = 0  # Если индекс выходит за пределы, начинаем с первого профиля

            profile = profiles[profile_index]
            driver.execute_script("arguments[0].scrollIntoView();", profile)
            profile.click()
            print(f"Профиль {profile_index + 1} выбран.")
            time.sleep(5)  # Задержка 5 секунд

            # Переход в раздел шансов
            go_to_chance_section(driver, invite1, invite2)

            # Обрабатываем мужчин
            process_men_and_check_messages(driver, invite1, invite2)

            # Обновляем страницу и переходим к следующему профилю
            driver.refresh()
            time.sleep(5)  # Задержка 5 секунд после обновления
            profile_index += 1

        except Exception as e:
            print(f"Ошибка при обработке профилей: {e}")
            break

# Переход в раздел шансов с проверкой кнопки "Messages"
def go_to_chance_section(driver, invite1, invite2):
    try:
        if stop_event.is_set():
            print("Остановка при переходе в раздел шансы по запросу.")
            return

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@data-testid='main-menu-item-Chance']"))).click()
        time.sleep(5)
        print("Переход в раздел шансы")

        if stop_event.is_set():
            print("Остановка при переходе в раздел шансы по запросу.")
            return

        # Проверяем и активируем чекбокс "Messages", если не активирован
        try:
            messages_checkbox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[text()='Messages']/preceding-sibling::span"))
            )
            checkbox_class = messages_checkbox.get_attribute("class")

            # Если чекбокс не содержит 'Mui-checked', кликаем по нему
            if 'Mui-checked' not in checkbox_class:
                print("Чекбокс 'Messages' не активирован. Активируем...")
                messages_checkbox.click()
                time.sleep(3)
                print("Чекбокс 'Messages' активирован.")
            else:
                print("Чекбокс 'Messages' уже активирован.")

        except NoSuchElementException:
            print("Чекбокс 'Messages' не найден.")

        # Нажимаем кнопку "Load more" до тех пор, пока она доступна
        while not stop_event.is_set():
            try:
                load_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'styles_clmn_2_chat_loadmore_btn__4PifQ')]"))
                )
                load_button.click()
                time.sleep(2)
                print("Нажата кнопка 'Load more'")
            except TimeoutException:
                print("Все шансы загружены.")
                break

    except Exception as e:
        print(f"Ошибка при переходе в раздел шансы: {e}")

# Функция отправки инвайта с использованием ActionChains
def send_invite_via_action_chains(driver, invite_text):
    chat_area = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/main/div/div[2]/div[2]/div[3]/div[3]/textarea'))
    )
    chat_area.clear()
    actions = ActionChains(driver)
    actions.move_to_element(chat_area).click().send_keys(invite_text).perform()
    time.sleep(1)
    chat_area.send_keys(Keys.ENTER)

def process_men_and_check_messages(driver, invite1, invite2):
    try:
        # Находим всех мужчин с классом чата
        men_with_chat = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[contains(@class, 'styles_clmn_2_chat_block_item__P6pxX styles_in_active__OJkLa')]"))
        )

        print(f"Найдено {len(men_with_chat)} мужчин с возможностью чата.")

        for index, man in enumerate(reversed(men_with_chat)):
            if stop_event.is_set():
                print("Остановка обработки мужчин по запросу.")
                break

            try:
                # Проверяем, есть ли кнопка "Maybe" (пропускаем таких мужчин)
                try:
                    maybe_button = man.find_element(By.XPATH, ".//div[@data-testid='set-maybe-btn']")
                    if 'active' in maybe_button.get_attribute("class"):
                        print(f"Мужчина {index + 1} имеет активированную кнопку 'Maybe'. Пропускаем.")
                        continue  # Пропускаем мужчину
                except NoSuchElementException:
                    pass

                print(f"Открываем чат с мужчиной {index + 1}...")
                driver.execute_script("arguments[0].scrollIntoView();", man)
                ActionChains(driver).move_to_element(man).click().perform()
                time.sleep(3)  # Ожидаем открытия чата

                if stop_event.is_set():
                    print("Остановка обработки мужчин по запросу.")
                    break

                # Проверяем наличие сообщений в чате
                chat_history = driver.find_elements(By.XPATH, "//div[contains(@class, 'styles_clmn_3_chat_list__c6Bey')]")
                if len(chat_history) == 0:
                    print(f"Чат пустой у мужчины {index + 1}, добавляем в Maybe.")
                    try:
                        # Ищем и нажимаем кнопку "Maybe"
                        maybe_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, ".//div[@data-testid='set-maybe-btn']"))
                        )
                        maybe_button.click()
                        print(f"Мужчина {index + 1} добавлен в Maybe.")
                    except NoSuchElementException:
                        print(f"Кнопка Maybe для мужчины {index + 1} не найдена.")
                    continue

                # Проверяем наличие инвайта в истории сообщений
                if any(invite1 in history.text for history in chat_history):
                    print(f"Первый инвайт '{invite1}' уже отправлен. Пропускаем.")
                    continue  # Пропускаем мужчину, если инвайт уже был отправлен

                # Проверяем наличие текста в поле сообщения
                chat_area = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/main/div/div[2]/div[2]/div[3]/div[3]/textarea'))
                )
                current_text = chat_area.get_attribute('value').strip()

                # Если текст отличается от инвайта, пропускаем мужчину
                if current_text and current_text != invite1:
                    print(f"Текст в поле чата отличается от инвайта. Пропускаем мужчину {index + 1}.")
                    continue

                # Отправляем первый инвайт, если его нет
                if not current_text or current_text == invite1:
                    print(f"Отправляем первый инвайт '{invite1}'.")
                    send_invite_via_action_chains(driver, invite1)
                else:
                    print(f"Первый инвайт уже отправлен.")

                # Проверка на наличие баннера ошибки
                try:
                    error_banner = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@data-testid='alertMain-modal']"))
                    )
                    print("Баннер ошибки получен. Готовимся отправить второй инвайт.")

                    # Очищаем поле ввода
                    chat_area.clear()
                    time.sleep(1)

                    # Используем функцию send_invite_via_action_chains для ввода invite2
                    actions = ActionChains(driver)
                    actions.move_to_element(chat_area).click().send_keys(invite2).perform()
                    time.sleep(1)

                    # Получаем текущий текст в поле ввода после ввода
                    current_text = chat_area.get_attribute('value').strip()

                    # Проверяем, совпадает ли введенный текст с invite2
                    if current_text == invite2:
                        print("Текст в поле ввода соответствует invite2. Отправляем второй инвайт.")
                        chat_area.send_keys(Keys.ENTER)
                        time.sleep(2)  # Задержка перед проверкой отправки
                        # Проверяем, отправлено ли сообщение
                        current_text = chat_area.get_attribute('value').strip()
                        if current_text == "":
                            print("Второй инвайт успешно отправлен.")
                        else:
                            print("После отправки второго инвайта поле ввода не пустое. Возможно, сообщение не было отправлено.")
                    else:
                        print("Текст в поле ввода не соответствует invite2. Второй инвайт не отправлен.")

                    # Закрываем баннер "Got it"
                    got_it_button = error_banner.find_element(By.XPATH, "//span[text()='Got it']")
                    got_it_button.click()
                    print("Баннер ошибки закрыт. Переход к следующему чату.")
                    continue  # Переходим к следующему мужчине
                except TimeoutException:
                    print("Баннер ошибки не появился.")

                # Проверка на кнопку "Like"
                try:
                    like_button = driver.find_element(By.XPATH, "//div[@data-testid='like-btn']")
                    like_button.click()
                    print("Кнопка 'Like' нажата.")
                except NoSuchElementException:
                    print("Кнопка 'Like' не найдена.")

            except Exception as e:
                print(f"Ошибка при обработке мужчины {index + 1}: {e}")
                continue

    except Exception as e:
        print(f"Ошибка при обработке мужчин с возможностью чата: {e}")

# Функция для остановки браузера
def stop_browser():
    global browser_instance
    global stop_event

    # Устанавливаем событие остановки
    stop_event.set()

    if browser_instance:
        browser_instance.quit()  # Закрытие браузера
        browser_instance = None  # Сбрасываем объект
        print("Браузер закрыт.")
    else:
        print("Браузер не был запущен.")

# Функция для проверки детектирования
def check_detect():
    global browser_instance
    if browser_instance is None:  # Проверяем, не запущен ли уже браузер
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--incognito")

        # Запуск браузера с опциями
        browser_instance = uc.Chrome(options=chrome_options)

        browser_instance.get('https://bot.sannysoft.com')
        time.sleep(10)
    else:
        print("Браузер уже запущен для проверки детектирования.")
