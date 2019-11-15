"""
异步任务
"""
from celery_task.main import app


@app.task
def test():
    print("测试函数")