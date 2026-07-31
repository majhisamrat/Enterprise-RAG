from celery import Celery
from app.config import settings

celery_app = Celery(
    "enterprise_rag_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # Force Redis RESP2 protocol to avoid 'unknown command HELLO 3' errors
    redis_backend_transport_options={"protocol": 2},
    broker_transport_options={"protocol": 2},
)
