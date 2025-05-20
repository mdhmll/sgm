from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Schedule, Group, Subject, User
from app import db
from datetime import datetime, time
from flask_wtf import FlaskForm

bp = Blueprint('schedule', __name__, url_prefix='/schedule')

# Словарь для отображения номеров дней недели на их названия
DAYS_OF_WEEK = {
    0: 'Понедельник',
    1: 'Вторник',
    2: 'Среда',
    3: 'Четверг',
    4: 'Пятница',
    5: 'Суббота',
    6: 'Воскресенье'
}

@bp.route('/')
@login_required
def index():
    # Получаем все группы для фильтрации
    groups = Group.query.all()
    
    # Получаем группу для фильтрации
    group_id = request.args.get('group_id', type=int)
    
    # Если пользователь студент, показываем расписание только для его групп
    if current_user.role == 'student':
        if not current_user.groups:
            flash('Вы не состоите ни в одной группе')
            return redirect(url_for('main.dashboard'))
        
        # Если группа не указана, берем первую группу студента
        if not group_id:
            group_id = current_user.groups[0].id
        
        # Проверяем, что студент состоит в указанной группе
        if group_id not in [group.id for group in current_user.groups]:
            flash('У вас нет доступа к расписанию этой группы')
            return redirect(url_for('main.dashboard'))
    
    # Если выбрана группа, фильтруем расписание по ней
    if group_id:
        schedules = Schedule.query.filter_by(group_id=group_id).order_by(Schedule.day_of_week, Schedule.start_time).all()
        selected_group = Group.query.get_or_404(group_id)
    else:
        schedules = Schedule.query.order_by(Schedule.day_of_week, Schedule.start_time).all()
        selected_group = None
    
    # Группируем расписание по дням недели
    schedule_by_day = {}
    for day in range(7):
        schedule_by_day[day] = [s for s in schedules if s.day_of_week == day]
    
    return render_template('schedule/index.html', 
                          schedule_by_day=schedule_by_day, 
                          days=DAYS_OF_WEEK, 
                          groups=groups, 
                          selected_group=selected_group)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    # Только администраторы и преподаватели могут добавлять расписание
    if current_user.role not in ['admin', 'teacher']:
        flash('У вас нет доступа к этой странице')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        day_of_week = int(request.form['day_of_week'])
        start_hour, start_minute = map(int, request.form['start_time'].split(':'))
        end_hour, end_minute = map(int, request.form['end_time'].split(':'))
        room = request.form['room']
        subject_id = int(request.form['subject_id'])
        group_id = int(request.form['group_id'])
        
        start_time = time(hour=start_hour, minute=start_minute)
        end_time = time(hour=end_hour, minute=end_minute)
        
        # Создаем новую запись в расписании
        schedule = Schedule(
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            room=room,
            subject_id=subject_id,
            group_id=group_id
        )
        
        db.session.add(schedule)
        db.session.commit()
        flash('Запись в расписании успешно добавлена')
        return redirect(url_for('schedule.index'))
    
    subjects = Subject.query.all()
    groups = Group.query.all()
    
    return render_template('schedule/add.html', 
                          subjects=subjects, 
                          groups=groups, 
                          days=DAYS_OF_WEEK)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    # Только администраторы и преподаватели могут редактировать расписание
    if current_user.role not in ['admin', 'teacher']:
        flash('У вас нет доступа к этой странице')
        return redirect(url_for('main.dashboard'))
    
    schedule = Schedule.query.get_or_404(id)
    
    # Преподаватели могут редактировать только свои предметы
    if current_user.role == 'teacher' and schedule.subject.teacher_id != current_user.id:
        flash('Вы можете редактировать только свои предметы')
        return redirect(url_for('schedule.index'))
    
    if request.method == 'POST':
        schedule.day_of_week = int(request.form['day_of_week'])
        start_hour, start_minute = map(int, request.form['start_time'].split(':'))
        end_hour, end_minute = map(int, request.form['end_time'].split(':'))
        schedule.start_time = time(hour=start_hour, minute=start_minute)
        schedule.end_time = time(hour=end_hour, minute=end_minute)
        schedule.room = request.form['room']
        schedule.subject_id = int(request.form['subject_id'])
        schedule.group_id = int(request.form['group_id'])
        
        db.session.commit()
        flash('Запись в расписании обновлена')
        return redirect(url_for('schedule.index'))
    
    subjects = Subject.query.all()
    groups = Group.query.all()
    
    # Форматирование времени для вывода в формате HH:MM
    start_time_str = f"{schedule.start_time.hour:02d}:{schedule.start_time.minute:02d}"
    end_time_str = f"{schedule.end_time.hour:02d}:{schedule.end_time.minute:02d}"
    
    return render_template('schedule/edit.html', 
                          schedule=schedule, 
                          subjects=subjects, 
                          groups=groups, 
                          days=DAYS_OF_WEEK,
                          start_time_str=start_time_str,
                          end_time_str=end_time_str)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    # Проверяем, что это POST-запрос и CSRF-токен действителен
    form = FlaskForm()
    if not form.validate():
        flash('Ошибка проверки CSRF-токена. Пожалуйста, попробуйте снова.', 'danger')
        return redirect(url_for('schedule.index'))

    # Только администраторы и преподаватели могут удалять расписание
    if current_user.role not in ['admin', 'teacher']:
        flash('У вас нет доступа к этой странице', 'danger')
        return redirect(url_for('main.dashboard'))
    
    schedule = Schedule.query.get_or_404(id)
    
    # Преподаватели могут удалять только свои предметы
    if current_user.role == 'teacher' and schedule.subject.teacher_id != current_user.id:
        flash('Вы можете удалять только свои предметы', 'danger')
        return redirect(url_for('schedule.index'))
    
    try:
        # Удаляем связанные записи посещаемости
        from app.models import Attendance
        Attendance.query.filter_by(schedule_id=schedule.id).delete()
        
        # Удаляем запись расписания
        db.session.delete(schedule)
        db.session.commit()
        flash('Запись в расписании успешно удалена', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении записи расписания: {str(e)}', 'danger')
    
    return redirect(url_for('schedule.index'))