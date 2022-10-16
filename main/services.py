import datetime

from telethon import TelegramClient, events
from .utils import parse_json_file_info
from .models import Dialog, User, Message, Info
from django.db import transaction
import asyncio
import os

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


def run(username, paths):
    user = User.objects.get(username=username)
    user_info = Info()
    user_info.user = user
    for path in paths:
        asyncio.run(run_load_dialogs(user, user_info, path))
    user.if_service = True
    user.save()
    user_info.save()


async def run_load_dialogs(user, user_info, path):
    app_id, app_hash, proxy_host, proxy_port = parse_json_file_info(path['json'])

    async def main():
        async for dialog in client.iter_dialogs():
            if dialog.is_user:
                user_info.all_dialogs+=1
                if dialog.unread_count == 0:
                    user_info.read_dialogs+=1
                d = Dialog(
                    user=user,
                    dialog_id=dialog.id,
                    file_name_of_session=path['session'],
                    title=dialog.name,
                    last_message=dialog.message.text,
                    is_last_message_out=dialog.message.out,
                    time=dialog.date
                )
                d.save()
                async for message in client.iter_messages(dialog):
                    m = Message(
                        dialog=d,
                        message_id=message.id,
                        message=message.text,
                        time=message.date,
                        is_sender=message.out
                    )
                    m.save()

    client = TelegramClient(path['session'], app_id, app_hash, proxy=('http', proxy_host, proxy_port))
    await client.connect()
    if not await client.is_user_authorized():
        user_info.not_loaded+=1
        return ''
    user_info.loaded+=1
    async with client:
        await main()


async def check_messages(username, path):
    app_id, app_hash, proxy_host, proxy_port = parse_json_file_info(path['json'])
    chats = [i[0] for i in Dialog.objects.filter(user__username=username).values_list('dialog_id')]
    client = TelegramClient(path['session'], app_id, app_hash, proxy=('http', proxy_host, proxy_port))

    @client.on(events.NewMessage(incoming=True, chats=chats))
    async def get_new_message(event):
        with transaction.atomic():
            mess = Message(
                dialog=Dialog.objects.get(dialog_id=event.message.peer_id),
                message_id=event.message.id,
                message=event.message.message,
                time=datetime.datetime.now(),
                is_sender=False
            )
            mess.save()

    client.start()
    client.run_until_disconnected()

