from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, Subject
from app import db
from flask_wtf import FlaskForm

bp = Blueprint('teacher', __name__, url_prefix='/teachers')

@bp.route('/')
@login_required
def index():
    # Только администраторы могут видеть список всех преподавателей
    if current_user.role != 'admin':
        flash('У вас нет доступа к этой странице', 'danger')
        return redirect(url_for('main.dashboard'))
    
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('teachers/index.html', teachers=teachers)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    # Только администраторы могут добавлять преподавателей
    if current_user.role != 'admin':
        flash('У вас нет доступа к этой странице', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        
        # Проверка существования пользователя
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Пользователь с таким именем уже существует', 'danger')
            return redirect(url_for('teacher.add'))
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Пользователь с таким email уже существует', 'danger')
            return redirect(url_for('teacher.add'))
        
        # Создание нового преподавателя
        teacher = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='teacher'
        )
        teacher.set_password(password)
        
        db.session.add(teacher)
        db.session.commit()
        flash('Преподаватель успешно добавлен', 'success')
        return redirect(url_for('teacher.index'))
    
    return render_template('teachers/add.html')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    # Только администраторы могут редактировать преподавателей
    if current_user.role != 'admin':
        flash('У вас нет доступа к этой странице', 'danger')
        return redirect(url_for('main.dashboard'))
    
    teacher = User.query.get_or_404(id)
    if teacher.role != 'teacher':
        flash('Пользователь не является преподавателем', 'danger')
        return redirect(url_for('teacher.index'))
    
    # Получаем предметы, которые ведет преподаватель
    subjects = Subject.query.filter_by(teacher_id=teacher.id).all()
    
    if request.method == 'POST':
        # Проверка уникальности нового имени пользователя
        if teacher.username != request.form['username']:
            existing = User.query.filter_by(username=request.form['username']).first()
            if existing:
                flash('Пользователь с таким именем уже существует', 'danger')
                return render_template('teachers/edit.html', teacher=teacher, subjects=subjects)
        
        # Проверка уникальности нового email
        if teacher.email != request.form['email']:
            existing = User.query.filter_by(email=request.form['email']).first()
            if existing:
                flash('Пользователь с таким email уже существует', 'danger')
                return render_template('teachers/edit.html', teacher=teacher, subjects=subjects)
        
        teacher.username = request.form['username']
        teacher.email = request.form['email']
        teacher.first_name = request.form['first_name']
        teacher.last_name = request.form['last_name']
        
        # Если указан новый пароль, изменяем его
        if request.form.get('password'):
            teacher.set_password(request.form['password'])
        
        db.session.commit()
        flash('Данные преподавателя успешно обновлены', 'success')
        return redirect(url_for('teacher.index'))
    
    return render_template('teachers/edit.html', teacher=teacher, subjects=subjects)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    # Проверяем, что это POST-запрос и CSRF-токен действителен
    form = FlaskForm()
    if not form.validate():
        flash('Ошибка проверки CSRF-токена. Пожалуйста, попробуйте снова.', 'danger')
        return redirect(url_for('teacher.index'))
        
    # Только администраторы могут удалять преподавателей
    if current_user.role != 'admin':
        flash('У вас нет доступа к этой странице', 'danger')
        return redirect(url_for('main.dashboard'))
    
    teacher = User.query.get_or_404(id)
    if teacher.role != 'teacher':
        flash('Пользователь не является преподавателем', 'danger')
        return redirect(url_for('teacher.index'))
    
    try:
        # Открепляем предметы от преподавателя
        subjects = Subject.query.filter_by(teacher_id=teacher.id).all()
        for subject in subjects:
            subject.teacher_id = None
        
        # Удаляем преподавателя
        db.session.delete(teacher)
        db.session.commit()
        flash('Преподаватель успешно удален', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении преподавателя: {str(e)}', 'danger')
    
    return redirect(url_for('teacher.index'))
