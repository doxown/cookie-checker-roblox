import os
import json
import requests
import subprocess
import sys
from datetime import datetime
from typing import Dict, Optional

class RobloxAccountManager:
    def __init__(self, data_file: str = "accounts.json"):
        self.data_file = data_file
        self.accounts = self.load_accounts()
        self.current_account = None
        
    def load_accounts(self) -> Dict:
        """Загружает данные аккаунтов из файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def save_accounts(self):
        """Сохраняет данные аккаунтов в файл"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, ensure_ascii=False, indent=2)
    
    def add_account(self, username: str, cookie: str, notes: str = ""):
        """Добавляет новый аккаунт"""
        if username in self.accounts:
            print(f"Аккаунт {username} уже существует!")
            return False
        
        self.accounts[username] = {
            'cookie': cookie,
            'added_date': datetime.now().isoformat(),
            'notes': notes,
            'last_used': None
        }
        self.save_accounts()
        print(f"Аккаунт {username} успешно добавлен!")
        return True
    
    def remove_account(self, username: str):
        """Удаляет аккаунт"""
        if username in self.accounts:
            del self.accounts[username]
            self.save_accounts()
            print(f"Аккаунт {username} удален!")
            return True
        print(f"Аккаунт {username} не найден!")
        return False
    
    def switch_account(self, username: str) -> bool:
        """Переключается на указанный аккаунт"""
        if username not in self.accounts:
            print(f"Аккаунт {username} не найден!")
            return False
        
        self.current_account = username
        self.accounts[username]['last_used'] = datetime.now().isoformat()
        self.save_accounts()
        print(f"Переключен на аккаунт {username}")
        return True
    
    def get_current_cookie(self) -> Optional[str]:
        """Получает cookie текущего аккаунта"""
        if self.current_account and self.current_account in self.accounts:
            return self.accounts[self.current_account]['cookie']
        return None
    
    def list_accounts(self):
        """Выводит список всех аккаунтов"""
        if not self.accounts:
            print("Нет сохраненных аккаунтов")
            return
        
        print("\n" + "="*50)
        print("СОХРАНЕННЫЕ АККАУНТЫ:")
        print("="*50)
        
        for idx, (username, data) in enumerate(self.accounts.items(), 1):
            last_used = data.get('last_used', 'Никогда')
            if last_used:
                try:
                    last_used = datetime.fromisoformat(last_used).strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            current_mark = " ← ТЕКУЩИЙ" if username == self.current_account else ""
            print(f"{idx}. {username}{current_mark}")
            print(f"   Добавлен: {data.get('added_date', 'Неизвестно')}")
            print(f"   Последнее использование: {last_used}")
            if data.get('notes'):
                print(f"   Заметки: {data['notes']}")
            print()
    
    def verify_cookie(self, cookie: str) -> bool:
        """Проверяет валидность cookie"""
        headers = {
            'Cookie': f'.ROBLOSECURITY={cookie}',
            'User-Agent': 'Mozilla/5.0'
        }
        
        try:
            response = requests.get(
                'https://users.roblox.com/v1/users/authenticated',
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def export_to_file(self, filename: str = "cookies_export.txt"):
        """Экспортирует cookies в текстовый файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            for username, data in self.accounts.items():
                f.write(f"Username: {username}\n")
                f.write(f"Cookie: {data['cookie']}\n")
                f.write(f"Added: {data.get('added_date', 'N/A')}\n")
                f.write("-" * 40 + "\n")
        print(f"Cookies экспортированы в {filename}")

def clear_screen():
    """Очищает экран консоли"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    """Основное меню"""
    manager = RobloxAccountManager()
    
    while True:
        clear_screen()
        print("="*50)
        print("ROBLOX ACCOUNT MANAGER")
        print("="*50)
        print("\n1. Добавить аккаунт")
        print("2. Удалить аккаунт")
        print("3. Переключить аккаунт")
        print("4. Список аккаунтов")
        print("5. Получить текущий cookie")
        print("6. Экспортировать cookies")
        print("7. Проверить cookie на валидность")
        print("8. Выход")
        
        choice = input("\nВыберите действие (1-8): ").strip()
        
        if choice == "1":
            clear_screen()
            print("ДОБАВЛЕНИЕ АККАУНТА")
            print("-" * 30)
            username = input("Введите username: ").strip()
            cookie = input("Введите ROBLOSECURITY cookie: ").strip()
            
            if not cookie.startswith("_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_"):
                print("Внимание: Cookie не похож на стандартный ROBLOSECURITY!")
                confirm = input("Все равно добавить? (y/n): ").lower()
                if confirm != 'y':
                    continue
            
            notes = input("Заметки (опционально): ").strip()
            manager.add_account(username, cookie, notes)
            input("\nНажмите Enter для продолжения...")
            
        elif choice == "2":
            clear_screen()
            print("УДАЛЕНИЕ АККАУНТА")
            print("-" * 30)
            manager.list_accounts()
            username = input("\nВведите username для удаления: ").strip()
            manager.remove_account(username)
            input("\nНажмите Enter для продолжения...")
            
        elif choice == "3":
            clear_screen()
            print("ПЕРЕКЛЮЧЕНИЕ АККАУНТА")
            print("-" * 30)
            manager.list_accounts()
            username = input("\nВведите username для переключения: ").strip()
            if manager.switch_account(username):
                cookie = manager.get_current_cookie()
                print(f"\nТекущий cookie для {username}:")
                print("-" * 40)
                print(cookie[:50] + "..." if len(cookie) > 50 else cookie)
            input("\nНажмите Enter для продолжения...")
            
        elif choice == "4":
            clear_screen()
            manager.list_accounts()
            input("\nНажмите Enter для продолжения...")
            
        elif choice == "5":
            clear_screen()
            cookie = manager.get_current_cookie()
            if cookie:
                print("ТЕКУЩИЙ COOKIE:")
                print("-" * 40)
                print(cookie)
                
                # Копирование в буфер обмена (опционально)
                try:
                    import pyperclip
                    pyperclip.copy(cookie)
                    print("\n✓ Cookie скопирован в буфер обмена!")
                except ImportError:
                    print("\nУстановите pyperclip для копирования в буфер")
            else:
                print("Аккаунт не выбран!")
            input("\nНажмите Enter для продолжения...")
            
        elif choice == "6":
            clear_screen()
            filename = input("Введите имя файла для экспорта (по умолчанию: cookies_export.txt): ").strip()
            if not filename:
                filename = "cookies_export.txt"
            manager.export_to_file(filename)
            input("\nНажмите Enter для продолжения...")
            
        elif choice == "7":
            clear_screen()
            print("ПРОВЕРКА COOKIE НА ВАЛИДНОСТЬ")
            print("-" * 40)
            cookie = input("Введите cookie для проверки: ").strip()
            if manager.verify_cookie(cookie):
                print("✓ Cookie валиден!")
            else:
                print("✗ Cookie невалиден или истек срок действия")
            input("\nНажмите Enter для продолжения...")
            
        elif choice == "8":
            print("Выход...")
            break
            
        else:
            print("Неверный выбор!")
            input("Нажмите Enter для продолжения...")

if __name__ == "__main__":
    # Создаем директорию для данных, если её нет
    os.makedirs("data", exist_ok=True)
    
    # Запускаем меню
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nПрограмма завершена пользователем")
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
        input("Нажмите Enter для выхода...")