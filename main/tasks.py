from config.celery import app
from .services import run, check_messages
from .models import User


@app.task
def run_loading(username, paths):
    run(username, paths)


@app.task
def run_check_messages(username, path):
    user = User.objects.get(username=username)
    if user.is_loading_process_started:
        raise Exception('The task is already running')
    else:
        user.is_loading_process_started = True
        user.save()
        check_messages(username, path)

