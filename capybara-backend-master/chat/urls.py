"""
The URL configuration of the chat module.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register),
    path('delete_account', views.delete_account),
    path('login', views.login),
    path('logout', views.logout),
    path('get_userinfo', views.get_userinfo),

    path('change_userinfo', views.change_userinfo),
    path('find_user/<username>', views.find_user),

    path('get_friend_list', views.get_friend_list),
    path('add_friend', views.add_friend),
    path('get_friend_request', views.get_friend_request),
    path('process_friend_request', views.process_friend_request),
    path('delete_friend', views.delete_friend),
    path('add_friend_tag', views.add_friend_tag),
    path('get_friend_list_by_tag/<tag>', views.get_friend_list_by_tag),

    path('conversation', views.conversation),
    path('message', views.message),
    path('read_conversation', views.read_conversation),
    path('delete_message', views.delete_message),

    path('group', views.group),
    path('manager', views.manager),
    path('master', views.master),
    path('remove_member', views.remove_member),
    path('group_notice', views.group_notice),
    path('invite', views.invite),
    path('group_request', views.group_request),
    path('process_group_request', views.process_group_request),
    path('leave_group', views.leave_group),
]
