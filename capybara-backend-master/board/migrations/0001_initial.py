# Generated by Django 4.1.3 on 2024-03-05 08:07

from django.db import migrations, models
import django.db.models.deletion
import utils.utils_time


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('board_state', models.TextField(max_length=2500)),
                ('board_name', models.CharField(max_length=255)),
                ('created_time', models.FloatField(default=utils.utils_time.get_timestamp)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('created_time', models.FloatField(default=utils.utils_time.get_timestamp)),
            ],
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['name'], name='board_user_name_0cc3e8_idx'),
        ),
        migrations.AddField(
            model_name='board',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='board.user'),
        ),
        migrations.AddIndex(
            model_name='board',
            index=models.Index(fields=['board_name'], name='board_board_board_n_958737_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='board',
            unique_together={('user', 'board_name')},
        ),
    ]
