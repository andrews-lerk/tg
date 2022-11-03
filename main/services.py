import datetime

from telethon import TelegramClient, events
from .models import Dialog, Message
from django.db import transaction
import os

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


async def run_load_dialogs(app_id, app_hash, proxy_host, proxy_port, user, path):
    async def main():
        async for dialog in client.iter_dialogs():
            if dialog.is_user:
                if dialog.name == 'Spam Info Bot' or dialog.name == 'Telegram':
                    continue
                try:
                    if dialog.message.text == None:
                        mess = '"Голосовое сообщение или медиа файл"'
                    else:
                        mess = dialog.message.text
                    d = Dialog(
                        user=user,
                        dialog_id=dialog.id,
                        file_name_of_session=path['session'],
                        title=dialog.name,
                        last_message=mess,
                        is_last_message_out=dialog.message.out,
                        time=dialog.date
                    )
                    d.save()
                except:
                    pass
                async for message in client.iter_messages(dialog):
                    try:
                        if message.text == None:
                            mess = '"Голосовое сообщение или медиа файл"'
                        else:
                            mess = message.text
                        m = Message(
                            dialog=d,
                            message_id=message.id,
                            message=mess,
                            time=message.date,
                            is_sender=message.out
                        )
                        m.save()
                    except:
                        pass

    client = TelegramClient(path['session'], app_id, app_hash, proxy=('http', proxy_host, proxy_port))
    await client.connect()
    if not await client.is_user_authorized():
        raise Exception('Session fail')
    async with client:
        await main()
        print('client on turned on!!!')

        @client.on(events.NewMessage(incoming=True))
        async def get_new_message(event):
            try:
                dialog = Dialog.objects.filter(dialog_id=event.chat_id).first()
                dialog.last_message = event.message.message
                dialog.time = datetime.datetime.now()
                dialog.is_last_message_out = False
                dialog.save()
                if event.message.message == None:
                    mess = '"Голосовое сообщение или медиа файл"'
                else:
                    mess = event.message.message
                mess = Message(
                    dialog=Dialog.objects.filter(dialog_id=event.chat_id).first(),
                    message_id=event.message.id,
                    message=mess,
                    time=datetime.datetime.now(),
                    is_sender=False
                )
                mess.save()
            except:
                pass

        await client.run_until_disconnected()


async def send_message(app_id, app_hash, proxy_host, proxy_port, path, dialog, mess):
    client = TelegramClient(path['session'], app_id, app_hash, proxy=('http', proxy_host, proxy_port))
    async with client:
        message = await client.send_message(dialog.dialog_id, mess)
        dialog.last_message = message.message
        dialog.time = datetime.datetime.now()
        dialog.is_last_message_out = True
        dialog.save()
        mess = Message(
            dialog=dialog,
            message_id=message.id,
            message=message.message,
            time=datetime.datetime.now(),
            is_sender=True
        )
        mess.save()

# async def check_messages(username, path):
#     app_id, app_hash, proxy_host, proxy_port = parse_json_file_info(path['json'])
#     chats = [i[0] for i in Dialog.objects.filter(user__username=username).values_list('dialog_id')]
#     client = TelegramClient(path['session'], app_id, app_hash, proxy=('http', proxy_host, proxy_port))
#     if not await client.is_user_authorized():
#         raise Exception('Session failed')
#
#     @client.on(events.NewMessage(incoming=True, chats=chats))
#     async def get_new_message(event):
#         with transaction.atomic():
#             mess = Message(
#                 dialog=Dialog.objects.get(dialog_id=event.message.peer_id),
#                 message_id=event.message.id,
#                 message=event.message.message,
#                 time=datetime.datetime.now(),
#                 is_sender=False
#             )
#             mess.save()
#     client.run_until_disconnected()
