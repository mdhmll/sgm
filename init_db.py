from app import create_app, db
from app.models.models import User, Group, Subject

# Создаем экземпляр приложения
app = create_app()

# Используем контекст приложения
with app.app_context():
    # Удаляем все существующие таблицы и создаем новые
    db.drop_all()
    db.create_all()
    print("База данных очищена и таблицы созданы заново.")
    
    # Создаем тестовых пользователей
    admin = User(
        username='admin',
        email='admin@example.com',
        first_name='Администратор',
        last_name='Системы',
        role='admin'
    )
    admin.set_password('admin')
    
    teacher = User(
        username='teacher',
        email='teacher@example.com',
        first_name='Иван',
        last_name='Преподавателев',
        role='teacher'
    )
    teacher.set_password('teacher')
    
    student = User(
        username='student',
        email='student@example.com',
        first_name='Петр',
        last_name='Студентов',
        role='student'
    )
    student.set_password('student')
    
    # Создаем тестовую группу
    group = Group(
        name='ИС-31',
        faculty='Информатика и вычислительная техника',
        year=3
    )
    
    # Добавляем студента в группу
    group.students.append(student)
    
    # Создаем тестовый предмет
    subject = Subject(
        name='Программирование',
        description='Основы программирования и алгоритмов',
        teacher=teacher
    )
    
    # Добавляем все в базу данных
    db.session.add(admin)
    db.session.add(teacher)
    db.session.add(student)
    db.session.add(group)
    db.session.add(subject)
    
    # Сохраняем изменения
    db.session.commit()
    
    print("Тестовые данные добавлены в базу данных.")
    print("Логины и пароли для тестовых аккаунтов:")
    print("Администратор: admin / admin")
    print("Преподаватель: teacher / teacher")
    print("Студент: student / student")