"""
celery_config：异步任务配置文件
"""

BROKER_URL = 'redis://localhost',  # 使用Redis作为消息代理
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0',  # 把任务结果存在了Redis
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24,  # 任务过期时间
