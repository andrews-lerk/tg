from django.contrib import admin
from .models import User, UserSessions, Dialog, Message, Info, WorkingTasks
from .forms import FilesForm


class SessionFilesInline(admin.StackedInline):
    model = UserSessions
    form = FilesForm
    extra = 0


class InfoInline(admin.StackedInline):
    model = Info
    extra = 0


class MessagesInline(admin.StackedInline):
    model = Message
    extra = 0


class WorkingTasksInline(admin.StackedInline):
    model = WorkingTasks
    extra = 0


class UserAdmin(admin.ModelAdmin):
    inlines = [SessionFilesInline, InfoInline, WorkingTasksInline]


class DialogAdmin(admin.ModelAdmin):
    inlines = [MessagesInline, ]


admin.site.register(User, UserAdmin)
admin.site.register(Dialog, DialogAdmin)
