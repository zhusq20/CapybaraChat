"""
The URL configuration of the board module.
"""
from django.urls import path
from board import views

urlpatterns = [
    path('startup', views.startup),
    path('login', views.login),
    path('boards', views.boards),
    path('boards/<index>', views.boards_index),
    path('user/<userName>', views.user_board),
]
