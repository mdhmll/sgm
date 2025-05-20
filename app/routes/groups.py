from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Group
from flask_wtf import FlaskForm

bp = Blueprint('groups', __name__, url_prefix='/groups')

@bp.route('/')
@login_required
def index():
    # Только администратор может управлять группами
    if current_user.role != 'admin':
        flash('У вас нет доступа к этой странице', 'danger')
        return redirect(url_for('main.dashboard'))
    
    groups = Group.query.order_by(Group.name).all()
    return render_template('groups/index.html', groups=groups)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    # Только администратор может добавлять группы
    if current_user.role != 'admin':
        flash('У вас нет доступа к этой странице', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        name = request.form['name']
        faculty = request.form['faculty']
        year = int(request.form['year'])
        
        # Проверка, существует ли группа с таким названием
        existing_group = Group.query.filter_by(name=name).first()
        if existing_group:
            flash('Группа с таким названием уже существует', 'danger')
            return render_template('groups/add.html')
        
        # Создание новой группы
        group = Group(
            name=name,
            faculty=faculty,
            year=year
        )
        
        db.session.add(group)
        db.session.commit()
        flash('Группа успешно добавлена', 'success')
        return redirect(url_for('groups.index'))
    
    return render_template('groups/add.html')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    # Только администратор может редактировать группы
    if current_user.role != 'admin':
        flash('У вас нет доступа к этой странице', 'danger')
        return redirect(url_for('main.dashboard'))
    
    group = Group.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form['name']
        faculty = request.form['faculty']
        year = int(request.form['year'])
        
        # Проверка, существует ли другая группа с таким названием
        existing_group = Group.query.filter_by(name=name).first()
        if existing_group and existing_group.id != id:
            flash('Группа с таким названием уже существует', 'danger')
            return render_template('groups/edit.html', group=group)
        
        # Обновление данных группы
        group.name = name
        group.faculty = faculty
        group.year = year
        
        db.session.commit()
        flash('Группа успешно обновлена', 'success')
        return redirect(url_for('groups.index'))
    
    return render_template('groups/edit.html', group=group)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    # Проверяем, что это POST-запрос и CSRF-токен действителен
    form = FlaskForm()
    if not form.validate():
        flash('Ошибка проверки CSRF-токена. Пожалуйста, попробуйте снова.', 'danger')
        return redirect(url_for('groups.index'))

    # Только администратор может удалять группы
    if current_user.role != 'admin':
        flash('У вас нет доступа к этой странице', 'danger')
        return redirect(url_for('main.dashboard'))
    
    group = Group.query.get_or_404(id)
    
    try:
        # Проверяем, есть ли у группы связанные данные
        if group.students or group.schedules.count() > 0:
            flash('Невозможно удалить группу, так как с ней связаны студенты или расписание', 'danger')
        else:
            db.session.delete(group)
            db.session.commit()
            flash('Группа успешно удалена', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении группы: {str(e)}', 'danger')
        
    return redirect(url_for('groups.index'))