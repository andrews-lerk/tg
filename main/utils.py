from config.settings import BASE_DIR, MEDIA_ROOT
import json


def parse_path(queryset):
    result = []
    for file in queryset:
        full_file = str(file.files).split('/')[-1]
        file_name = full_file.split('.')[0]
        file_type = full_file.split('.')[-1]
        if file_type == 'json':
            for s_file in queryset:
                session_full = str(s_file.files).split('/')[-1]
                session_name = session_full.split('.')[0]
                session_type = session_full.split('.')[-1]
                if file_name == session_name and session_type == 'session':
                    json_full_path = str(BASE_DIR / MEDIA_ROOT / str(file.files))
                    session_full_path = str(BASE_DIR / MEDIA_ROOT / str(s_file.files))
                    result.append({'json': json_full_path,
                                   'session': session_full_path})
    return result


def parse_json_file_info(path):
    with open(path) as f:
        data = json.loads(f.read())
    return data['app_id'], data['app_hash'], data['proxy'][1], data['proxy'][2]

