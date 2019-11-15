"""
celery:主函数
"""
from celery import Celery

app = Celery('celery_task', include=['celery_task.task'])
app.config_from_object('celery.celery_config')


if __name__ == '__main__':
    # 启动celery 命令
    # celery -A celery.app_test worker -l info
    app.start()
