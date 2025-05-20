import webview
import threading
import sys
import os
import logging
from app import create_app

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация Flask-приложения
flask_app = create_app()

def start_flask():
    """
    Запускает Flask-сервер в отдельном потоке
    """
    try:
        # Запуск на локальном хосте на порту 5000
        flask_app.run(host='127.0.0.1', port=5000, threaded=True)
    except Exception as e:
        logger.error(f"Ошибка запуска Flask: {e}")
        sys.exit(1)

def main():
    # Запуск Flask в отдельном потоке
    t = threading.Thread(target=start_flask)
    t.daemon = True
    t.start()
    
    # Создание окна с веб-содержимым
    webview.create_window(
        title='Школьное Приложение',
        url='http://127.0.0.1:5000',
        width=1200,
        height=800,
        resizable=True,
        min_size=(800, 600),
        background_color='#FFFFFF',
        text_select=True
    )
      # Запуск основного цикла GUI
    webview.start(debug=False)
    
    # После закрытия окна
    logger.info("Приложение закрыто")
    sys.exit(0)

if __name__ == '__main__':
    main()
