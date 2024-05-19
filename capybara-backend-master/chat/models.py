from django.db import models

# Create your models here.
class UserInfo(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=16, unique=True)
    password = models.CharField(max_length=64)
    nickname = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True)

class Friend(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserInfo, related_name='self', on_delete=models.CASCADE)
    friend = models.ForeignKey(UserInfo, related_name='friends', on_delete=models.CASCADE)
    tag = models.CharField(max_length=20, blank=True)

def get_sentinel_user():
    return UserInfo.objects.get_or_create(
        username="DELETED_USER",
        password="",
        phone="",
        email=""
    )[0]

class Conversation(models.Model):
    TYPE_CHOICES = [
        (0, 'private chat'),
        (1, 'group chat')
    ]

    id = models.AutoField(primary_key=True)
    type = models.IntegerField(choices=TYPE_CHOICES)
    members = models.ManyToManyField(
        UserInfo, related_name='conversations',
        # on_delete=models.SET(get_sentinel_user)
    )

class Message(models.Model):
    id = models.AutoField(primary_key=True)
    conversation = models.ForeignKey(
        Conversation, related_name='messages',
        on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        UserInfo, related_name='sent_messages',
        on_delete=models.SET(get_sentinel_user)
    )
    # receivers = models.ManyToManyField(
    #     UserInfo, related_name='received_messages',
    #     on_delete=models.SET(get_sentinel_user)
    # )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    reply_to = models.IntegerField(default=-1)
    reply_by = models.IntegerField(default=0)
    notice = models.IntegerField(default=0)

class ReadMessage(models.Model):
    id = models.AutoField(primary_key=True)
    conversation = models.ForeignKey(
        Conversation, related_name='read_messages',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        UserInfo, related_name='read_messages',
        on_delete=models.SET(get_sentinel_user)
    )
    fro = models.IntegerField(default=-1)
    to = models.IntegerField(default=-1)

class DeletedMessage(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(UserInfo, related_name='deleted_messages', on_delete=models.CASCADE)
    deleted = models.ManyToManyField(Message, related_name='deleted_messages', blank=True)

class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)
    conversation = models.ForeignKey(Conversation, related_name='group', on_delete=models.CASCADE)
    master = models.ForeignKey(
        UserInfo, related_name='group_master', on_delete=models.SET(get_sentinel_user)
    )
    manager = models.ManyToManyField(UserInfo, related_name='group_manager', blank=True)
    notice = models.ManyToManyField(Message, related_name='group', blank=True)

class Request(models.Model):
    TYPE_CHOICES = [
        (0, 'friend request'),
        (1, 'group request'),
        (2, 'group invitation'),
    ]

    STATUS_CHOICES = [
        ('Accept', 'accept'),
        ('Reject', 'reject'),
        ('Pending', 'pending'),
    ]

    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(
        UserInfo, related_name='sent_requests',
        on_delete=models.SET(get_sentinel_user)
    )
    receiver = models.ForeignKey(
        UserInfo, related_name='received_requests',
        on_delete=models.SET(get_sentinel_user), blank=True, null=True
    )
    group = models.ForeignKey(
        Group, related_name='requests',
        on_delete=models.CASCADE, blank=True, null=True
    )
    type = models.IntegerField(choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    timestamp = models.DateTimeField(auto_now=True, db_index=True)
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.CASCADE)
