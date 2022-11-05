import asyncio
import sqlite3
from django.shortcuts import render, redirect
from .forms import LoginForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .models import UserSessions, User, Dialog, Message
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
    dialogs = Dialog.objects.filter(user=user).order_by('-time')
    all_dialogs_value = len(dialogs)
    not_read_dialogs_value = len(dialogs.filter(is_read=False))
    context = {
        'dialogs': dialogs,
        'all': all_dialogs_value,
        'not_read': not_read_dialogs_value
    }
    return render(request, 'lk.html', context)


@login_required()
def lk_not_read(request):
    user = User.objects.get(username=request.user)
    dialogs = Dialog.objects.filter(user=user, is_read=False).order_by('-time')
    not_read_dialogs_value = len(dialogs.filter(is_read=False))
    context = {
        'dialogs': dialogs,
        'all': 0,
        'not_read': not_read_dialogs_value
    }
    return render(request, 'lk.html', context)


@login_required()
def lk_only_in(request):
    user = User.objects.get(username=request.user)
    dialogs = Dialog.objects.filter(user=user, is_last_message_out=False).order_by('-time')
    context = {
        'dialogs': dialogs,
        'all': 0,
        'not_read': 0
    }
    return render(request, 'lk.html', context)


def run_loading(username, paths):
    for path in paths:
        run.delay(username, path)


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

    dialog = Dialog.objects.get(id=pk)
    if not dialog.is_read:
        dialog.is_read = True
        dialog.save()

    messages = Message.objects.filter(dialog__id=pk).order_by('time')
    context = {
        'messages': messages,
    }
    return render(request, 'dialog.html', context)
