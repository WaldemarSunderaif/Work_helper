# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Main.py'],  # Главный файл программы
    pathex=[],  # Дополнительные пути для поиска зависимостей (если нужно)
    binaries=[],  # Бинарные файлы (если есть)
    datas=[('Chance.py', '.'), ('.env', '.')],  # Включение других файлов: Chance.py и .env
    hiddenimports=[],  # Если нужно включить скрытые импорты
    hookspath=[],  # Пути к hook-скриптам (если есть)
    hooksconfig={},
    runtime_hooks=[],  # Hooks для запуска программы (если нужно)
    excludes=[],  # Исключаемые модули (если есть)
    noarchive=False,  # Оставить архив с исходным кодом в сборке
    optimize=0,  # Уровень оптимизации (0 или 1)
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],  # Сюда можно добавлять дополнительные библиотеки, если нужно
    name='Main_Test_1.01',  # Название исполняемого файла
    debug=False,  # Отключаем режим отладки
    bootloader_ignore_signals=False,
    strip=False,  # Оставить отладочные символы (False, чтобы не уменьшать размер бинарника)
    upx=True,  # Используем UPX для сжатия (True - включено)
    upx_exclude=[],  # Исключения для UPX сжатия (если нужно)
    runtime_tmpdir=None,  # Временная директория (None - не требуется)
    console=False,  # Отключить консольное окно (True, если требуется консоль)
    disable_windowed_traceback=False,  # Показать ошибку в случае сбоя программы
    argv_emulation=False,  # Использовать для запуска приложений на Mac (не требуется для Windows)
    target_arch=None,  # Архитектура целевой системы (None - по умолчанию)
    codesign_identity=None,  # Подпись (если требуется)
    entitlements_file=None,  # Файл прав доступа (если требуется)
)
