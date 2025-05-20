from app.models.models import User, Group, Subject, Schedule, Attendance, Grade

# Функция для загрузки пользователя по ID для Flask-Login
from app import login_manager

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))