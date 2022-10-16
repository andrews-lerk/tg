from django.shortcuts import render, redirect
from .forms import LoginForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from .models import UserSessions, User, Info, Dialog, Message
from .utils import parse_path
from .tasks import run_loading, run_check_messages


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
    if not user.if_service:
        if not user.is_loading_process_started:
            run_loading.delay(user.username, paths)
            user.is_loading_process_started = True
            user.save()
            return render(request, 'loading.html')
        else:
            return render(request, 'loading.html')
    info = Info.objects.get(user=user)
    dialogs = Dialog.objects.filter(user=user)
    context = {
        'info': info,
        'dialogs': dialogs
    }
    return render(request, 'lk.html', context)

def dialog(request, pk):
    return render(request, 'dialog.html')


def run_messages_checker(request):
    user = User.objects.get(username=request.user)
    run_check_messages.delay(user.username, UserSessions.objects.get(user=user).files.path)
    return HttpResponse(status=200)

