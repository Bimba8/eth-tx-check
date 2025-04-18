import requests
import xlsxwriter # type: ignore
from time import sleep

# Настройки
API_KEY = "YOUR_API_KEY"  # Замените на ваш Etherscan API ключ
WALLETS_FILE = "wallets.txt"
OUTPUT_EXCEL = "wallets_transactions.xlsx"
BASE_URL = "https://api.etherscan.io/api"

def read_wallets(file_path):
    """Читает адреса кошельков из файла."""
    try:
        with open(file_path, "r") as file:
            wallets = [line.strip() for line in file if line.strip()]
        return wallets
    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
        return []

def get_transactions_count(wallet_address):
    """Получает количество транзакций для адреса через Etherscan API."""
    params = {
        "module": "account",
        "action": "txlist",
        "address": wallet_address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": API_KEY
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "1" and data["message"] == "OK":
            transactions = data["result"]
            return len(transactions), True
        elif data["message"] == "No transactions found":
            return 0, False
        else:
            print(f"Ошибка для адреса {wallet_address}: {data['message']}")
            return 0, False
    except requests.RequestException as e:
        print(f"Ошибка запроса для адреса {wallet_address}: {e}")
        return 0, False

def main():
    # Чтение кошельков
    wallets = read_wallets(WALLETS_FILE)
    if not wallets:
        print("Нет адресов для обработки.")
        return
    
    # Создание Excel-файла
    workbook = xlsxwriter.Workbook(OUTPUT_EXCEL)
    worksheet = workbook.add_worksheet()
    
    # Заголовки
    headers = ["№ кошелька", "Адрес кошелька", "Есть ли транзакции", "Количество транзакций"]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
    
    # Обработка кошельков
    for idx, wallet in enumerate(wallets, 1):
        print(f"Обработка кошелька {idx}: {wallet}")
        
        # Получение данных о транзакциях
        tx_count, has_tx = get_transactions_count(wallet)
        
        # Запись данных в Excel
        worksheet.write(idx, 0, idx)  # № кошелька
        worksheet.write(idx, 1, wallet)  # Адрес кошелька
        worksheet.write(idx, 2, "Да" if has_tx else "Нет")  # Есть ли транзакции
        worksheet.write(idx, 3, tx_count if has_tx else 0)  # Количество транзакций
        
        # Задержка для соблюдения лимитов API
        sleep(0.2)
    
    # Сохранение и закрытие файла
    workbook.close()
    print(f"Результаты сохранены в {OUTPUT_EXCEL}")

if __name__ == "__main__":
    main()
