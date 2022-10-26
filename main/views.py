import asyncio
import sqlite3
import time

from django.shortcuts import render, redirect
from .forms import LoginForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from .models import UserSessions, User, Info, Dialog, Message, WorkingTasks
from .utils import parse_path, parse_json_file_info
from .tasks import run
from .services import send_message


def login_view(request):
    form = LoginForm
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request=request,
                                username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is None:
                form.add_error('password', 'Введенные данные не корректны, попробуйте еще раз ')
                context = {
                    'form': form
                }
                return render(request, 'login.html', context)
            login(request, user)
            return redirect(reverse('messages'))
    context = {
        'form': form
    }
    return render(request, 'login.html', context)


@login_required()
def lk(request):
    files = UserSessions.objects.filter(user=request.user)
    paths = parse_path(files)
    user = User.objects.get(username=request.user)
    if not user.is_loading_process_started:
        run_loading(user.username, paths)
        user.is_loading_process_started = True
        user.save()
    # info = Info.objects.get(user=user)
    dialogs = Dialog.objects.filter(user=user).order_by('-time')
    context = {
        # 'info': info,
        'dialogs': dialogs
    }
    return render(request, 'lk.html', context)


def run_loading(username, paths):
    for path in paths:
        task = run.delay(username, path)
        WorkingTasks.objects.create(
            user=User.objects.get(username=username),
            task_uid=task.id
        )


@login_required()
def dialog(request, pk):
    if request.method == "POST":
        dialog = Dialog.objects.get(id=pk)
        mess = request.POST.get('mess')
        session_file = dialog.file_name_of_session
        json_file = session_file.split('.')[0]+'.json'
        paths = {
            'json': json_file,
            'session': session_file
        }
        app_id, app_hash, proxy_host, proxy_port = parse_json_file_info(paths['json'])
        while True:
            try:
                asyncio.run(send_message(app_id, app_hash, proxy_host, proxy_port, paths, dialog, mess))
                break
            except sqlite3.OperationalError:
                continue
        return redirect('dialog', pk)

    messages = Message.objects.filter(dialog__id=pk).order_by('time')
    context = {
        'messages': messages,
    }
    return render(request, 'dialog.html', context)

# def run_messages_checker(request):
#     user = User.objects.get(username=request.user)
#     run_check_messages.delay(user.username, UserSessions.objects.get(user=user).files.path)
#     return HttpResponse(status=200)
