from django.urls import path, include
from .views import *

urlpatterns = [
    path('', login_view, name='login'),
    path('messages', lk, name='messages'),
    path('dialog/<int:pk>', dialog, name='dialog'),
    path('messages/not_read', lk_not_read, name='messages-unread'),
    path('messages/only-in', lk_only_in, name='messages-in')
]
