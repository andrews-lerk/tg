from config.celery import app
from .services import run


@app.task
def run_loading(username, paths):
    run(username, paths)
