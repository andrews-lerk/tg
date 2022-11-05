from config.celery import app
from .models import User
from .services import run_load_dialogs
import asyncio
from .utils import parse_json_file_info


@app.task
def run(username, path):
    user = User.objects.get(username=username)
    app_id, app_hash, proxy_host, proxy_port = parse_json_file_info(path['json'])
    try:
        loop = asyncio.get_running_loop()
    except:
        loop = asyncio.new_event_loop()
    loop.create_task(run_load_dialogs(app_id, app_hash, proxy_host, proxy_port, user, path, loop))
    try:
        loop.run_forever()
    except:
        pass
