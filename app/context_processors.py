"""
Контекст-процессоры для шаблонов Flask.
"""
from flask_wtf.csrf import generate_csrf

def csrf_processor():
    """
    Добавляет CSRF-токен к контексту всех шаблонов.
    """
    return {'csrf_token': generate_csrf()}
