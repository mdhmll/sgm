import os
from app import create_app, db
from app.models.models import User, Group, Subject, Schedule, Attendance, Grade
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Group': Group, 
        'Subject': Subject, 
        'Schedule': Schedule, 
        'Attendance': Attendance, 
        'Grade': Grade
    }