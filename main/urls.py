from django.urls import path, include
from .views import *

urlpatterns = [
    path('', login_view, name='login'),
    path('messages', lk, name='messages'),
    path('dialog/<int:pk>', dialog, name='dialog'),
]