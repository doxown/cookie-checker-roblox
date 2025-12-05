import os
from pathlib import Path

# Пути к файлам
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"
COOKIES_EXPORT_DIR = DATA_DIR / "exports"

# Создаем директории при необходимости
DATA_DIR.mkdir(exist_ok=True)
COOKIES_EXPORT_DIR.mkdir(exist_ok=True)

# Настройки безопасности
ENCRYPTION_ENABLED = False  # Включить для шифрования cookies
ENCRYPTION_KEY = None  # Ключ шифрования (если ENCRYPTION_ENABLED = True)