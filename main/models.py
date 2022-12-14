import os

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .managers import UserManager
from config.celery import app


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=255, unique=True)
    date_joined = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    date_expired = models.DateTimeField(_('Дата окончания пользования'), auto_now_add=False, null=True)
    is_active = models.BooleanField(_('active'), default=False)
    is_staff = models.BooleanField(_('staff'), default=False)
    if_service = models.BooleanField(_('Обслуживание пользователя'), default=False)
    is_loading_process_started = models.BooleanField(_('Поцесс загрузки диалогов запущен'), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('Личный кабинет клиента')
        verbose_name_plural = _('Личные кабинеты клиентов')

    def save(self, *args, **kwargs):
        if not self.is_superuser:
            if not self.is_active:
                self.set_password(self.password)
                self.is_active = True
        return super().save()


class UserSessions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    files = models.FileField(upload_to=f'session_files/%Y_%m_%d_%H_%M')

    class Meta:
        verbose_name = _('Аккаунт ТГ')
        verbose_name_plural = _('Аккаунты ТГ')

    def delete(self, using=None, keep_parents=True):
        try:
            os.remove(str(self.files.path))
        except:
            pass
        super().delete()


class Dialog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    dialog_id = models.BigIntegerField()
    file_name_of_session = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    user_name = models.CharField(max_length=511)
    phone_number = models.CharField(max_length=127)
    last_message = models.TextField()
    is_last_message_out = models.BooleanField()
    is_read = models.BooleanField()
    time = models.DateTimeField()

    class Meta:
        verbose_name = _('Диалог')
        verbose_name_plural = _('Все диалоги')

    def get_absolute_url(self):
        return reverse('dialog', args=[self.pk])


class Message(models.Model):
    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE)

    message_id = models.BigIntegerField()
    message = models.TextField()
    time = models.DateTimeField()
    is_sender = models.BooleanField()
