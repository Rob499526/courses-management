from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    'app',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
)

celery_app.conf.beat_schedule = {
    'check-course-deadlines-every-day': {
        'task': 'app.tasks.check_course_deadlines',
        'schedule': crontab(hour=0, minute=0),
    },
}

celery_app.conf.timezone = 'UTC'

import app.tasks
