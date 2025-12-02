from notifications_service.app.core.config import rabbit_settings
from celery import Celery


celery_app = Celery(
    "notifications_service",
    broker=rabbit_settings.RABBITMQ_URL,
)

celery_app.conf.task_routes = {
    "users.*": {"queue": "users"},
    "staff.*": {"queue": "staff"},
}

celery_app.autodiscover_tasks(
    [
        "notifications_service.app.tasks.users",
        "notifications_service.app.tasks.staff",
    ],
)
