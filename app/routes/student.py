from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, Group
from app import db
from flask_wtf import FlaskForm

bp = Blueprint('student', __name__, url_prefix='/students')

@bp.route('/')
@login_required
def index():
    # Только администраторы и преподаватели могут видеть список всех студентов
    if current_user.role not in ['admin', 'teacher']:
        flash('У вас нет доступа к этой странице')
        return redirect(url_for('main.dashboard'))
    
    students = User.query.filter_by(role='student').all()
    groups = Group.query.all()
    return render_template('students/index.html', students=students, groups=groups)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    # Только администраторы могут добавлять студентов
    if current_user.role != 'admin':
        flash('У вас нет доступа к этой странице')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        group_id = request.form.get('group_id')
        
        # Проверка существования пользователя
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Пользователь с таким именем уже существует')
            return redirect(url_for('student.add'))
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Пользователь с таким email уже существует')
            return redirect(url_for('student.add'))
        
        # Создание нового студента
        student = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='student'
        )
        student.set_password(password)
        
        db.session.add(student)
        
        # Добавление студента в группу, если указана
        if group_id:
            group = Group.query.get(group_id)
            if group:
                group.students.append(student)
        
        db.session.commit()
        flash('Студент успешно добавлен')
        return redirect(url_for('student.index'))
    
    groups = Group.query.all()
    return render_template('students/add.html', groups=groups)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    # Только администраторы могут редактировать студентов
    if current_user.role != 'admin':
        flash('У вас нет доступа к этой странице')
        return redirect(url_for('main.dashboard'))
    
    student = User.query.get_or_404(id)
    if student.role != 'student':
        flash('Пользователь не является студентом')
        return redirect(url_for('student.index'))
    
    if request.method == 'POST':
        student.username = request.form['username']
        student.email = request.form['email']
        student.first_name = request.form['first_name']
        student.last_name = request.form['last_name']
        
        # Если указан новый пароль, изменяем его
        if request.form.get('password'):
            student.set_password(request.form['password'])
        
        # Обновление групп
        for group in student.groups:
            group.students.remove(student)
        
        group_id = request.form.get('group_id')
        if group_id:
            group = Group.query.get(group_id)
            if group:
                group.students.append(student)
        
        db.session.commit()
        flash('Данные студента обновлены')
        return redirect(url_for('student.index'))
    
    groups = Group.query.all()
    return render_template('students/edit.html', student=student, groups=groups)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    # Проверяем, что это POST-запрос и CSRF-токен действителен
    form = FlaskForm()
    if not form.validate():
        flash('Ошибка проверки CSRF-токена. Пожалуйста, попробуйте снова.', 'danger')
        return redirect(url_for('student.index'))

    # Только администраторы могут удалять студентов
    if current_user.role != 'admin':
        flash('У вас нет доступа к этой странице', 'danger')
        return redirect(url_for('main.dashboard'))
    
    student = User.query.get_or_404(id)
    if student.role != 'student':
        flash('Пользователь не является студентом', 'danger')
        return redirect(url_for('student.index'))
    
    try:
        # Удаляем связи с группами
        for group in student.groups:
            group.students.remove(student)
        
        # Удаляем связанные записи
        from app.models import Attendance, Grade
        Attendance.query.filter_by(student_id=student.id).delete()
        Grade.query.filter_by(student_id=student.id).delete()
        
        # Удаляем студента
        db.session.delete(student)
        db.session.commit()
        flash('Студент успешно удален', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении студента: {str(e)}', 'danger')
    
    return redirect(url_for('student.index'))