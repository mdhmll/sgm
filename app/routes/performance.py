from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, Subject, Schedule, Attendance, Grade, Group
from app import db
from datetime import datetime, date

bp = Blueprint('performance', __name__, url_prefix='/performance')

# Функция для расчета среднего балла
def calculate_average_grade(grades):
    if not grades:
        return 0
    return round(sum(grade.value for grade in grades) / len(grades), 2)

@bp.route('/')
@login_required
def index():
    # Получаем параметры для фильтрации
    group_id = request.args.get('group_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    
    # Получаем списки для фильтров
    groups = Group.query.all()
    subjects = Subject.query.all()
    
    # Проверка роли пользователя и соответствующие действия
    if current_user.role == 'student':
        # Студент может видеть только свою успеваемость
        student = current_user
        grades = Grade.query.filter_by(student_id=student.id)
        
        if subject_id:
            grades = grades.filter_by(subject_id=subject_id)
        
        grades = grades.order_by(Grade.date.desc()).all()
       
        # Рассчитываем средний балл по предметам
        subject_grades = {}
        for grade in grades:
            if grade.subject_id not in subject_grades:
                subject_grades[grade.subject_id] = []
            subject_grades[grade.subject_id].append(grade)
        
        subject_averages = {subject_id: calculate_average_grade(subject_grades[subject_id]) 
                         for subject_id in subject_grades}
        
        return render_template('performance/student.html', 
                              student=student, 
                              grades=grades, 
                              subjects=subjects,
                              subject_averages=subject_averages,
                              overall_average=calculate_average_grade(grades))
    
    elif current_user.role == 'teacher':
        # Преподаватель может видеть успеваемость по своим предметам
        teacher_subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
        
        if not teacher_subjects:
            flash('У вас нет назначенных предметов')
            return redirect(url_for('main.dashboard'))
        
        if not subject_id:
            subject_id = teacher_subjects[0].id
        
        # Проверка, что предмет принадлежит преподавателю
        if subject_id not in [s.id for s in teacher_subjects]:
            flash('Вы не ведете этот предмет')
            return redirect(url_for('performance.index'))
        
        students = []
        grades = []
        
        if group_id:
            group = Group.query.get_or_404(group_id)
            students = group.students
            
            # Получаем оценки студентов группы по выбранному предмету
            grades = Grade.query.filter_by(subject_id=subject_id).\
                filter(Grade.student_id.in_([s.id for s in students])).\
                order_by(Grade.date.desc()).all()
        
        return render_template('performance/teacher.html', 
                              groups=groups, 
                              subjects=teacher_subjects, 
                              selected_group_id=group_id,
                              selected_subject_id=subject_id,
                              students=students,
                              grades=grades)
    
    else:  # Администратор
        students = []
        grades = []
        
        # Если выбрана группа, получаем её студентов
        if group_id:
            group = Group.query.get_or_404(group_id)
            students = group.students
            
            if subject_id:
                # Если выбран предмет, получаем оценки студентов по предмету
                grades = Grade.query.filter_by(subject_id=subject_id).\
                    filter(Grade.student_id.in_([s.id for s in students])).\
                    order_by(Grade.date.desc()).all()
        
        return render_template('performance/admin.html', 
                              groups=groups, 
                              subjects=subjects, 
                              selected_group_id=group_id,
                              selected_subject_id=subject_id,
                              students=students,
                              grades=grades)

@bp.route('/add_grade', methods=['GET', 'POST'])
@login_required
def add_grade():
    # Только администраторы и преподаватели могут добавлять оценки
    if current_user.role not in ['admin', 'teacher']:
        flash('У вас нет доступа к этой странице')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        student_id = int(request.form['student_id'])
        subject_id = int(request.form['subject_id'])
        value = int(request.form['value'])
        comment = request.form['comment']
        grade_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        
        # Проверка, что преподаватель ведет этот предмет
        if current_user.role == 'teacher':
            subject = Subject.query.get_or_404(subject_id)
            if subject.teacher_id != current_user.id:
                flash('Вы не можете добавлять оценки по этому предмету')
                return redirect(url_for('performance.index'))
        
        # Создаем новую оценку
        grade = Grade(
            student_id=student_id,
            subject_id=subject_id,
            value=value,
            date=grade_date,
            comment=comment
        )
        
        db.session.add(grade)
        db.session.commit()
        flash('Оценка успешно добавлена')
        return redirect(url_for('performance.index', subject_id=subject_id))
    
    # Получаем данные для формы
    group_id = request.args.get('group_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    student_id = request.args.get('student_id', type=int)
    
    if current_user.role == 'teacher':
        subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    else:
        subjects = Subject.query.all()
    
    groups = Group.query.all()
    
    if group_id:
        students = Group.query.get_or_404(group_id).students
    else:
        students = User.query.filter_by(role='student').all()
    
    return render_template('performance/add_grade.html',
                          groups=groups,
                          subjects=subjects,
                          students=students,
                          selected_group_id=group_id,
                          selected_subject_id=subject_id,
                          selected_student_id=student_id,
                          today=date.today().strftime('%Y-%m-%d'))

@bp.route('/edit_grade/<int:grade_id>', methods=['GET', 'POST'])
@login_required
def edit_grade(grade_id):
    # Только администраторы и преподаватели могут редактировать оценки
    if current_user.role not in ['admin', 'teacher']:
        flash('У вас нет доступа к этой странице')
        return redirect(url_for('main.dashboard'))
    
    # Получаем оценку по ID
    grade = Grade.query.get_or_404(grade_id)
    
    # Проверка, что преподаватель ведет этот предмет
    if current_user.role == 'teacher':
        if grade.subject.teacher_id != current_user.id:
            flash('Вы не можете редактировать оценки по этому предмету')
            return redirect(url_for('performance.index'))
    
    if request.method == 'POST':
        value = int(request.form['value'])
        comment = request.form['comment']
        grade_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        
        # Обновляем оценку
        grade.value = value
        grade.date = grade_date
        grade.comment = comment
        
        db.session.commit()
        flash('Оценка успешно обновлена')
        return redirect(url_for('performance.index', subject_id=grade.subject_id))
      # Получаем данные для формы
    subject = grade.subject
    student = grade.student
    
    return render_template('performance/edit_grade.html',
                          grade=grade,
                          subject=subject,
                          student=student,
                          date_value=grade.date.strftime('%Y-%m-%d'))

@bp.route('/view_grade/<int:grade_id>')
@login_required
def view_grade(grade_id):
    # Получаем оценку по ID
    grade = Grade.query.get_or_404(grade_id)
    
    # Студенты могут видеть только свои оценки, преподаватели - оценки по своим предметам
    if current_user.role == 'student':
        if grade.student_id != current_user.id:
            flash('Вы можете просматривать только свои оценки')
            return redirect(url_for('performance.index'))
    
    # Получаем данные для отображения
    subject = grade.subject
    
    return render_template('performance/view_grade.html',
                          grade=grade,
                          subject=subject)

@bp.route('/delete_grade/<int:grade_id>', methods=['POST'])
@login_required
def delete_grade(grade_id):
    # Только администраторы и преподаватели могут удалять оценки
    if current_user.role not in ['admin', 'teacher']:
        flash('У вас нет доступа к этой странице')
        return redirect(url_for('main.dashboard'))
    
    # Получаем оценку по ID
    grade = Grade.query.get_or_404(grade_id)
    
    # Проверка, что преподаватель ведет этот предмет
    if current_user.role == 'teacher':
        if grade.subject.teacher_id != current_user.id:
            flash('Вы не можете удалять оценки по этому предмету')
            return redirect(url_for('performance.index'))
    
    subject_id = grade.subject_id
    
    # Удаляем оценку
    db.session.delete(grade)
    db.session.commit()
    flash('Оценка успешно удалена')
    
    return redirect(url_for('performance.index', subject_id=subject_id))

@bp.route('/attendance')
@login_required
def attendance():
    # Получаем параметры для фильтрации
    group_id = request.args.get('group_id', type=int)
    schedule_id = request.args.get('schedule_id', type=int)
    date_str = request.args.get('date')
    
    # Словарь дней недели
    days = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}
    
    # Парсим дату, если указана
    if date_str:
        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            attendance_date = date.today()
    else:
        attendance_date = date.today()
    
    # Для студента показываем только его посещаемость
    if current_user.role == 'student':
        attendances = Attendance.query.filter_by(student_id=current_user.id).order_by(Attendance.date.desc()).all()
        return render_template('performance/student_attendance.html', attendances=attendances, days=days)
    
    # Для преподавателя и администратора
    groups = Group.query.all()
    schedules = []
    students = []
    attendances = []
    
    # Если выбрана группа, получаем расписание для нее
    if group_id:
        group = Group.query.get_or_404(group_id)
        
        # Получаем все занятия для группы
        if current_user.role == 'teacher':
            # Для преподавателя только его предметы
            teacher_subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
            schedules = Schedule.query.filter_by(group_id=group_id).\
                filter(Schedule.subject_id.in_([s.id for s in teacher_subjects])).all()
        else:
            schedules = Schedule.query.filter_by(group_id=group_id).all()
        
        # Если нет расписания для группы
        if not schedules:
            flash('Нет расписания для выбранной группы')
            return redirect(url_for('performance.attendance'))
        
        # Если не выбрано конкретное занятие, берем первое
        if not schedule_id and schedules:
            schedule_id = schedules[0].id
        
        # Получаем студентов группы
        students = group.students
        
        # Получаем посещаемость для выбранного занятия и даты
        if schedule_id:
            schedule = Schedule.query.get_or_404(schedule_id)
            
            # Проверяем, что преподаватель ведет этот предмет
            if current_user.role == 'teacher' and schedule.subject.teacher_id != current_user.id:
                flash('Вы не ведете этот предмет')
                return redirect(url_for('performance.attendance'))
            
            attendances = Attendance.query.\
                filter_by(schedule_id=schedule_id, date=attendance_date).\
                all()
            
            # Создаем словарь для быстрого доступа к посещаемости по ID студента
            attendance_by_student = {a.student_id: a for a in attendances}
    
    return render_template('performance/attendance.html',
                          groups=groups,
                          schedules=schedules,
                          students=students,
                          attendances=attendances,
                          selected_group_id=group_id,
                          selected_schedule_id=schedule_id,
                          attendance_date=attendance_date,
                          days=days,  # Добавляем словарь дней недели
                          today=date.today().strftime('%Y-%m-%d'))

@bp.route('/record_attendance', methods=['POST'])
@login_required
def record_attendance():
    # Только администраторы и преподаватели могут отмечать посещаемость
    if current_user.role not in ['admin', 'teacher']:
        flash('У вас нет доступа к этой странице')
        return redirect(url_for('main.dashboard'))
    
    schedule_id = int(request.form['schedule_id'])
    attendance_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Преподаватели могут отмечать посещаемость только для своих предметов
    if current_user.role == 'teacher' and schedule.subject.teacher_id != current_user.id:
        flash('Вы не можете отмечать посещаемость для этого предмета')
        return redirect(url_for('performance.attendance'))
    
    # Получаем всех студентов группы
    group = Group.query.get_or_404(schedule.group_id)
    students = group.students
    
    # Удаляем предыдущие записи о посещаемости для этого занятия и даты
    Attendance.query.filter_by(schedule_id=schedule_id, date=attendance_date).delete()
    
    # Записываем новые данные о посещаемости
    for student in students:
        status = request.form.get(f'attendance_{student.id}') == 'on'
        attendance = Attendance(
            student_id=student.id,
            schedule_id=schedule_id,
            date=attendance_date,
            status=status
        )
        db.session.add(attendance)
    
    db.session.commit()
    flash('Посещаемость успешно записана')
    
    return redirect(url_for('performance.attendance', 
                           group_id=schedule.group_id, 
                           schedule_id=schedule_id, 
                           date=attendance_date.strftime('%Y-%m-%d')))