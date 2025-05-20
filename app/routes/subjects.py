from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Subject, User
from flask_wtf import FlaskForm

bp = Blueprint('subjects', __name__, url_prefix='/subjects')

@bp.route('/')
@login_required
def index():
    # Только администратор может управлять предметами
    if current_user.role != 'admin':
        flash('У вас нет доступа к этой странице', 'danger')
        return redirect(url_for('main.dashboard'))
    
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('subjects/index.html', subjects=subjects)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    # Только администратор может добавлять предметы
    if current_user.role != 'admin':
        flash('У вас нет доступа к этой странице', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Получаем всех преподавателей для выбора
    teachers = User.query.filter_by(role='teacher').order_by(User.last_name).all()
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        teacher_id = int(request.form['teacher_id']) if request.form['teacher_id'] else None
        
        # Проверка, существует ли предмет с таким названием
        existing_subject = Subject.query.filter_by(name=name).first()
        if existing_subject:
            flash('Предмет с таким названием уже существует', 'danger')
            return render_template('subjects/add.html', teachers=teachers)
        
        # Создание нового предмета
        subject = Subject(
            name=name,
            description=description,
            teacher_id=teacher_id
        )
        
        db.session.add(subject)
        db.session.commit()
        flash('Предмет успешно добавлен', 'success')
        return redirect(url_for('subjects.index'))
    
    return render_template('subjects/add.html', teachers=teachers)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    # Только администратор может редактировать предметы
    if current_user.role != 'admin':
        flash('У вас нет доступа к этой странице', 'danger')
        return redirect(url_for('main.dashboard'))
    
    subject = Subject.query.get_or_404(id)
    
    # Получаем всех преподавателей для выбора
    teachers = User.query.filter_by(role='teacher').order_by(User.last_name).all()
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        teacher_id = int(request.form['teacher_id']) if request.form['teacher_id'] else None
        
        # Проверка, существует ли другой предмет с таким названием
        existing_subject = Subject.query.filter_by(name=name).first()
        if existing_subject and existing_subject.id != id:
            flash('Предмет с таким названием уже существует', 'danger')
            return render_template('subjects/edit.html', subject=subject, teachers=teachers)
        
        # Обновление данных предмета
        subject.name = name
        subject.description = description
        subject.teacher_id = teacher_id
        
        db.session.commit()
        flash('Предмет успешно обновлен', 'success')
        return redirect(url_for('subjects.index'))
    
    return render_template('subjects/edit.html', subject=subject, teachers=teachers)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    # Проверяем, что это POST-запрос и CSRF-токен действителен
    form = FlaskForm()
    if not form.validate():
        flash('Ошибка проверки CSRF-токена. Пожалуйста, попробуйте снова.', 'danger')
        return redirect(url_for('subjects.index'))

    # Только администратор может удалять предметы
    if current_user.role != 'admin':
        flash('У вас нет доступа к этой странице', 'danger')
        return redirect(url_for('main.dashboard'))
    
    subject = Subject.query.get_or_404(id)
    
    try:
        # Проверяем, есть ли у предмета связанные данные
        if subject.schedules.count() > 0 or subject.grades.count() > 0:
            flash('Невозможно удалить предмет, так как с ним связаны расписание или оценки', 'danger')
        else:
            db.session.delete(subject)
            db.session.commit()
            flash('Предмет успешно удален', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении предмета: {str(e)}', 'danger')
    
    return redirect(url_for('subjects.index'))
