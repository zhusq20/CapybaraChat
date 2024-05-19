# Generated by Django 4.1.3 on 2024-05-13 14:58

import chat.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0009_message_notice_group_request_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='managers',
            field=models.ManyToManyField(related_name='received_group_requests', to='chat.userinfo'),
        ),
        migrations.AlterField(
            model_name='request',
            name='receiver',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET(chat.models.get_sentinel_user), related_name='received_requests', to='chat.userinfo'),
        ),
    ]
