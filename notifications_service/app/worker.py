import os
from celery import Celery


celery_app = Celery(
    "notifications_service",
    broker=os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672//"),
)

celery_app.conf.task_routes = {
    "notifications_service.app.tasks.send_email": {"queue": "emails"},
}

celery_app.autodiscover_tasks(["notifications_service.app.tasks"])
