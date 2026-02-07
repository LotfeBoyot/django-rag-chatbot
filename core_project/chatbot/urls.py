from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_endpoint, name='chat_endpoint'),
    path('', views.chat_page, name='chat_page'),
]