from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
import os
from config import Config

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    # Настройка приложения из класса конфигурации
    app.config.from_object(Config)
      # Инициализация расширений с приложением
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
      # Включаем защиту CSRF для всех форм
    csrf.init_app(app)
    
    # Создаем контекст приложения для использования расширений
    with app.app_context():
        csrf._exempt_views = set()    # Регистрируем контекст-процессор для автоматического добавления CSRF-токена
    from app.context_processors import csrf_processor
    app.context_processor(csrf_processor)
      # Регистрация маршрутов
    from app.routes import main, auth, student, schedule, performance, groups, subjects, teacher
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(student.bp)
    app.register_blueprint(schedule.bp)
    app.register_blueprint(performance.bp)
    app.register_blueprint(groups.bp)
    app.register_blueprint(subjects.bp)
    app.register_blueprint(teacher.bp)
      # Регистрируем обработчик ошибок CSRF
    from flask_wtf.csrf import CSRFError
    
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('csrf_error.html', reason=e.description), 400
    
    # Создаем папку для базы данных, если она еще не существует
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    return app