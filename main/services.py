import asyncio
import datetime

from django.utils import timezone
from telethon import TelegramClient, events
from .models import Dialog, Message
import os

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


async def run_load_dialogs(app_id, app_hash, proxy_host, proxy_port, user, path, loop):
    async def main():
        async for dialog in client.iter_dialogs():
            if dialog.is_user:
                if dialog.name == 'Spam Info Bot' or dialog.name == 'Telegram':
                    continue
                if dialog.entity.username is None:
                    username = 'Не удалось получить юзернейм'
                else:
                    username = dialog.entity.username
                if dialog.entity.phone is None:
                    phone = 'Телефон скрыт'
                else:
                    phone = dialog.entity.phone
                try:
                    if dialog.message.message is None:
                        mess = '"Голосовое сообщение или медиа файл"'
                    else:
                        mess = dialog.message.text
                    d = Dialog(
                        user=user,
                        dialog_id=dialog.id,
                        file_name_of_session=path['session'],
                        title=dialog.name,
                        user_name=username,
                        phone_number=phone,
                        last_message=mess,
                        is_last_message_out=dialog.message.out,
                        is_read=dialog.message.out,
                        time=dialog.date
                    )
                    d.save()
                except:
                    pass
                async for message in client.iter_messages(dialog):
                    try:
                        if message.message is None:
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

    async def clock(client, user):
        attempts = 1
        while True:
            if timezone.now() > user.date_expired:
                print(f'Disconnect client and delete user attempt {attempts}')
                await client.disconnect()
                if client.is_connected():
                    if attempts>=5:
                        print('disconnect not success!!! attempts more than 5')
                        break
                    attempts+=1
                    await client.disconnect()
                    continue
                await asyncio.sleep(60)
                try:
                    user.delete()
                except:
                    print('user already deleted')
                break
            await asyncio.sleep()
        return

    loop.create_task(clock(client, user))
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
                dialog.is_read = False
                dialog.save()
                if event.message.message is None:
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
        dialog.is_read = True
        dialog.save()
        mess = Message(
            dialog=dialog,
            message_id=message.id,
            message=message.message,
            time=datetime.datetime.now(),
            is_sender=True
        )
        mess.save()
