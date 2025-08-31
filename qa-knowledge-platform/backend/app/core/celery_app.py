from celery import Celery
from app.core.config import settings

# 创建Celery应用
celery_app = Celery(
    "qa-knowledge-platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.modules.news.tasks",
        "app.modules.users.tasks",
    ]
)

# Celery配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟
    task_soft_time_limit=25 * 60,  # 25分钟
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# 定时任务配置
celery_app.conf.beat_schedule = {
    "crawl-news-daily": {
        "task": "app.modules.news.tasks.crawl_news_sources",
        "schedule": 3600.0,  # 每小时执行一次
    },
}