from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import User, UserSessions, WorkingTasks
from .utils import parse_path
from telethon.sessions import MemorySession


@receiver(pre_delete, sender=User)
def my_handler(sender, instance: User, **kwargs):
    sessions = UserSessions.objects.filter(user=instance)
    paths = parse_path(sessions)
    for path in paths:
        conn = MemorySession()
        conn.close()
    for s in sessions:
        s.delete()
    tasks = WorkingTasks.objects.filter(user=instance)
    for t in tasks:
        t.delete()
