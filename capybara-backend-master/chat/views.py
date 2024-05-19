import json
from typing import Any
from django.http import HttpRequest
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from channels.layers import get_channel_layer, InMemoryChannelLayer
from asgiref.sync import async_to_sync

from chat.models import UserInfo, Friend, Request,\
    Conversation, Message, ReadMessage, DeletedMessage, Group
from utils.utils_require import CheckRequire, require
from utils.utils_request import request_success, request_failed
from utils.utils_jwt import generate_jwt_token, check_jwt_token

# Create your views here.

def check_username(body: dict, blank: bool = False):
    username = require(
        body, 'username', 'string',
        err_msg='Missing or error type of [username]'
            if not blank else 'Error type of [username]',
        blank=blank
    )
    if blank and username is None:
        return None
    assert 0 < len(username) <= 16, 'Bad length of [username]'
    assert ' ' not in username, 'Invalid char in [username]'
    user = UserInfo.objects.filter(username=username).first()
    if user is not None:
        raise KeyError('[username] has been registered', 1, 403)
    return username

def check_password(body: dict, blank: bool = False):
    password = require(
        body, 'password', 'string',
        err_msg='Missing or error type of [password]'
            if not blank else 'Error type of [password]',
        blank=blank
    )
    if blank and password is None:
        return None
    assert len(password) == 64, 'Bad length of [password]'
    return password

def check_phone(body: dict, blank: bool = False):
    phone = require(
        body, 'phone', 'string',
        err_msg='Missing or error type of [phone]'
            if not blank else 'Error type of [phone]',
        blank=blank
    )
    if blank and phone is None:
        return None
    assert 0 < len(phone) <= 11, 'Bad length of [phone]'
    assert phone.isdigit(), 'Invalid char in [phone]'
    user = UserInfo.objects.filter(phone=phone).first()
    if user is not None:
        raise KeyError('[phone] has been registered', 1, 403)
    return phone

def check_email(body: dict, blank: bool = False):
    email = require(
        body, 'email', 'string',
        err_msg='Missing or error type of [email]'
            if not blank else 'Error type of [email]',
        blank=blank
    )
    if blank and email is None:
        return None
    user = UserInfo.objects.filter(email=email).first()
    if user is not None:
        raise KeyError('[email] has been registered', 1, 403)
    return email

@require_POST
@CheckRequire
def register(req: HttpRequest):
    body = json.loads(req.body.decode('utf-8'))
    username = check_username(body)
    password = check_password(body)
    phone = check_phone(body)
    email = check_email(body)

    UserInfo.objects.create(username=username, password=password, phone=phone, email=email)
    return request_success()

@require_http_methods(['DELETE'])
@CheckRequire
def delete_account(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)

    body = json.loads(req.body.decode('utf-8'))
    password = require(body, 'password', 'string', err_msg='Missing or error type of [username]')
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"
    if password != user.password:
        return request_failed(1, "Wrong password", 401)

    # TODO: break WebSocket connection
    user.delete()
    return request_success()

@require_POST
@CheckRequire
def login(req: HttpRequest):
    body = json.loads(req.body.decode('utf-8'))
    username = require(body, 'username', 'string', err_msg='Missing or error type of [username]')
    password = require(body, 'password', 'string', err_msg='Missing or error type of [password]')
    user = UserInfo.objects.filter(username=username).first()
    if user is None:
        return request_failed(1, 'Invalid username', 404)
    if user.password == password:
        # TODO: establish WebSocket connection
        nickname = user.nickname if user.nickname != '' else user.username
        email = user.email
        return request_success({
            "token": generate_jwt_token(username),
            "nickname": nickname,
            "email": email
        })
    return request_failed(1, "Wrong password", 401)

@require_POST
@CheckRequire
def logout(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)

    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    if user is None:
        return request_failed(1, "Invalid username", 401)
    # TODO: break WebSocket connection
    return request_success()

@require_POST
@CheckRequire
def change_userinfo(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)

    body = json.loads(req.body.decode('utf-8'))
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    old_password = require(
        body, 'old_password', 'string',
        err_msg='Missing or error type of [password]'
    )
    if old_password != user.password:
        return request_failed(1, "Wrong password", 401)

    if nickname := require(
        body, 'nickname', 'string',
        err_msg='Error type of [nickname]',
        blank=True
    ):
        assert len(nickname) <= 20, 'Bad length of [nickname]'
        user.nickname = nickname

    if phone := check_phone(body, blank=True):
        user.phone = phone

    if email := check_email(body, blank=True):
        user.email = email

    if password := check_password(body, blank=True):
        user.password = password

    if username := check_username(body, blank=True):
        user.username = username
        # TODO: break WebSocket connection

    user.save()
    return request_success()

@require_GET
@CheckRequire
def get_userinfo(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)

    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    return request_success({
        "userinfo": {
            "username": user.username,
            "nickname": user.nickname,
            "phone": user.phone,
            "email": user.email
        }
    })

@require_GET
@CheckRequire
def find_user(req: HttpRequest, username: Any):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)

    cur_user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert cur_user is not None, "USER NOT FOUND"

    name = require(
        {"username": username}, 'username', 'string',
        err_msg='Bad param [username]'
    )
    assert 0 < len(name) <= 16, 'Bad param [username]'

    user = UserInfo.objects.filter(username=name).first()
    if user is None:
        return request_failed(1, 'User not found', 404)

    return request_success({
        "userinfo": {
            "username": user.username,
            "nickname": user.nickname,
            "phone": user.phone,
            "email": user.email
        }
    })

@require_GET
@CheckRequire
def get_friend_list(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    friends = Friend.objects.prefetch_related('user', 'friend').filter(user=user)
    friend_list = []
    for friendship in friends:
        friend_info = friendship.friend
        friend_list.append({
            "username": friend_info.username,
            "email": friend_info.email,
            "tag": friendship.tag
        })
    return request_success({
        "friends": friend_list
    })

@require_POST
@CheckRequire
def add_friend(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    body = json.loads(req.body.decode('utf-8'))
    name = require(body, 'friendname', 'string', err_msg='Missing or error type of [friendname]')
    assert 0 < len(name) <= 16, 'Bad length of [friendname]'
    assert name != user.username, 'Cannot add yourself as friend'

    friend = UserInfo.objects.filter(username=name).first()
    assert friend is not None, ("User not found", 1, 404)

    assert Friend.objects.filter(user=user, friend=friend).first() is None, (
        "User has been your friend", 1, 400
    )

    requests = Request.objects.prefetch_related('sender', 'receiver').filter(
        type=0, sender=user, receiver=friend
    )
    if len(requests) > 0:
        requests.delete()

    Request.objects.create(sender=user, receiver=friend, type=0, status='Pending')
    channel_layer: InMemoryChannelLayer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        friend.username,
        {'type': 'notify', 'message': 'new friend request'}
    )
    return request_success()

@require_GET
@CheckRequire
def get_friend_request(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    received_requests = Request.objects.prefetch_related(
        'sender', 'receiver'
    ).filter(type=0, receiver=user)
    sent_requests = Request.objects.prefetch_related(
        'sender', 'receiver'
    ).filter(type=0, sender=user)

    friends = []
    for request in received_requests:
        friends.append({
            "username": request.sender.username,
            "nickname": request.sender.nickname,
            "email": request.sender.email,
            "status": request.status,
            "role": "receiver",
            "timestamp": request.timestamp
            })
    for request in sent_requests:
        friends.append({
            "username": request.receiver.username,
            "nickname": request.receiver.nickname,
            "email": request.receiver.email,
            "status": request.status,
            "role": "sender",
            "timestamp": request.timestamp
        })
    friends.sort(key=lambda x: x['timestamp'])

    return request_success({"friends": friends})

@require_POST
@CheckRequire
def process_friend_request(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    body = json.loads(req.body.decode('utf-8'))
    friendname = require(
        body, 'friendname', 'string',
        err_msg='Missing or error type of [friendname]'
    )
    assert 0 < len(friendname) <= 16, 'Bad length of [friendname]'

    decision = require(body, 'decision', 'string', err_msg='Missing or error type of [decision]')
    assert decision in ['Accept', 'Reject'], 'Bad param [decision]'

    request = Request.objects.prefetch_related('sender', 'receiver').filter(
        type=0, sender__username=friendname, receiver=user
    ).first()

    if request is None:
        return request_failed(1, "Friend request not found", 404)

    if request.status != "Pending":
        return request_failed(1, "Friend request has been processed", 400)

    if decision == "Accept":
        Friend.objects.create(user=user, friend=request.sender)
        Friend.objects.create(user=request.sender, friend=user)
        request.status = "Accept"
        request.save()

        channel_layer: InMemoryChannelLayer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            request.sender.username,
            {'type': 'notify', 'message': f'new friend added {user.username}'}
        )
    else:
        request.status = "Reject"
        request.save()
    return request_success()

@require_POST
@CheckRequire
def delete_friend(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    body = json.loads(req.body.decode('utf-8'))
    name = require(body, 'friendname', 'string', err_msg='Missing or error type of [friendname]')
    assert 0 < len(name) <= 16, 'Bad length of [friendname]'

    friend = UserInfo.objects.filter(username=name).first()
    assert friend is not None, ("User not found", 1, 404)

    friendship0 = Friend.objects.filter(user=user, friend=friend)
    assert friendship0 is not None, (
        "User is not your friend", 1, 400
    )
    friendship0.delete()

    friendship1 = Friend.objects.filter(user=friend, friend=user)
    assert friendship1 is not None, (
        "User is not your friend", 1, 400
    )
    friendship1.delete()

    return request_success()

@require_POST
@CheckRequire
def add_friend_tag(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    body = json.loads(req.body.decode('utf-8'))

    tag = require(body, 'tag', 'string', err_msg='Missing or error type of [tag]')
    assert 0 < len(tag) <= 20, 'Bad length of [tag]'

    friend_list = require(
        body, 'friend_list', 'list[string]',
        err_msg='Missing or error type of [friendname]'
    )
    friends: list[Friend] = []
    for name in friend_list:
        assert 0 < len(name) <= 16, 'Bad length of [friendname]'
        friend = UserInfo.objects.filter(username=name).first()
        assert friend is not None, ("User not found", 1, 404)
        friendship = Friend.objects.filter(user=user, friend=friend).first()
        assert friendship is not None, (
            "User is not your friend", 1, 400
        )
        friends.append(friendship)

    for friendship in friends:
        friendship.tag = tag
        friendship.save()
    return request_success()

@require_GET
@CheckRequire
def get_friend_list_by_tag(req: HttpRequest, tag: str):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    tag = require(
        {"tag": tag}, 'tag', 'string',
        err_msg='Missing or error type of [tag]'
    )
    assert 0 < len(tag) <= 20, 'Bad length of [tag]'

    friends = Friend.objects.prefetch_related('user', 'friend').filter(user=user, tag=tag)
    friend_list = []
    for friendship in friends:
        friend_info = friendship.friend
        friend_list.append({
            "username": friend_info.username,
            "email": friend_info.email,
            "tag": friendship.tag
        })
    return request_success({
        "friends": friend_list
    })

@require_http_methods(['GET', 'POST'])
@CheckRequire
def conversation(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    if req.method == "POST":
        body = json.loads(req.body.decode('utf-8'))
        conv_type = require(body, 'type', 'int', err_msg='Missing or error type of [type]')
        assert conv_type in [0, 1], 'Bad param [type]'

        usernames = require(
            body, 'members', 'list[string]',
            err_msg='Missing or error type of [members]'
        )
        if conv_type == 0 and len(usernames) != 2:
            return request_failed(1, 'Bad param [members]', 400)
        members = []
        for username in usernames:
            if username == user.username:
                members.append(user)
            else:
                friendship = Friend.objects.filter(user=user, friend__username=username).first()
                assert friendship is not None, 'Bad param [members]'
                members.append(friendship.friend)

        if conv_type == 0:
            for conv in Conversation.objects.all():
                if conv.type == 0 and all([
                    member in conv.members.all() for member in members
                ]):
                    return request_success({
                        "conversation": format_conversation(conv)
                    })

        conv = Conversation.objects.create(type=conv_type)
        conv.members.set(members)

        for member in members:
            ReadMessage.objects.get_or_create(
                conversation=conv,
                user=member
            )

        return request_success({
            "conversation": format_conversation(conv)
        })

    else:
        conv_id = req.GET.get('id')
        if conv_id is None:
            conv_list = []
            for conv in Conversation.objects.all():
                if user in conv.members.all():
                    conv_list.append(format_conversation(conv))
            return request_success({
                "conversations": conv_list
            })

        conv_id = require({"id": conv_id}, 'id', 'int', err_msg='Missing or error type of [id]')
        conv = Conversation.objects.filter(id=conv_id).first()
        if user not in conv.members.all():
            return request_failed(1, 'Bad param [id]', 400)
        return request_success({
            "conversations": [format_conversation(conv),]
        })

@require_http_methods(['POST', 'GET'])
@CheckRequire
def message(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    if req.method == "POST":
        body = json.loads(req.body.decode('utf-8'))
        conv_id = require(
            body, 'conversation', 'int',
            err_msg='Missing or error type of [conversation]'
        )
        conv = Conversation.objects.filter(id=conv_id).first()
        assert conv is not None, 'Bad param [conversation]'
        if user not in conv.members.all():
            return request_failed(1, 'Bad param [conversation]', 400)
        if conv.type == 0:
            for member in conv.members.all():
                if member != user:
                    receiver = member
                    break
            friendship = Friend.objects.filter(user=user, friend=receiver).first()
            assert friendship is not None, 'User is not your friend'

        content = require(body, 'content', 'string', err_msg='Missing or error type of [content]')

        reply_to = require(body, 'reply_to', 'int', err_msg='Missing or error type of [reply_to]')
        if reply_to != -1:
            reply_message = Message.objects.filter(id=reply_to, notice=0).first()
            assert reply_message is not None, 'Bad param [reply_to]'
            if reply_message.conversation.id != conv_id:
                return request_failed(1, 'Bad param [reply_to]', 400)
            reply_message.reply_by += 1
            reply_message.save()

        message = Message.objects.create(
            conversation=conv,
            sender=user,
            content=content,
            reply_to=reply_to
        )
        # message.receivers.set(conv.members.all())

        channel_layer: InMemoryChannelLayer = get_channel_layer()
        for member in conv.members.all():
            if member != user:
                async_to_sync(channel_layer.group_send)(
                    member.username,
                    {'type': 'notify', 'message': f'new message in conversation {conv_id}'}
                )

        return request_success({
            'message': format_message(message)
        })

    else:
        conv_id = req.GET.get('conversation')
        after = req.GET.get('after')
        conv_id = require(
            {'id': conv_id}, 'id', 'int',
            err_msg='Missing or error type of [conversation]'
        )
        conv = Conversation.objects.filter(id=conv_id).first()
        assert conv is not None, 'Bad param [conversation]'
        assert user in conv.members.all(), 'Bad param [conversation]'

        after = require(
            {'id': after}, 'id', 'int',
            err_msg='Missing or error type of [after]'
        )
        messages = Message.objects.filter(conversation=conv, id__gt=after, notice=0)
        deleted_list = DeletedMessage.objects.get_or_create(user=user)[0].deleted.all()

        last_read = ReadMessage.objects.filter(conversation=conv, user=user).first()
        messages = messages.filter(id__gt=last_read.fro)
        # unread = 0
        unread = Message.objects.filter(conversation=conv, id__gt=last_read.to, notice=0).count()
        # for message in Message.objects.filter(conversation=conv):
        #     if message.id > last_read.to:
        #         unread += 1
        return request_success({
            'unread': unread,
            'messages': [
                format_message(message) for message in messages if message not in deleted_list
            ]
        })

@require_POST
@CheckRequire
def read_conversation(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    body = json.loads(req.body.decode('utf-8'))
    conv_id = require(
        body, 'conversation', 'int',
        err_msg='Missing or error type of [conversation]'
    )
    conv = Conversation.objects.filter(id=conv_id).first()
    assert conv is not None, 'Bad param [conversation]'
    assert user in conv.members.all(), 'Bad param [conversation]'

    read_message = ReadMessage.objects.filter(conversation=conv, user=user).first()
    assert read_message is not None, 'Bad param [conversation]'

    last_message = Message.objects.filter(conversation=conv, notice=0).order_by('id').last()
    read_message.to = last_message.id
    read_message.save()

    channel_layer: InMemoryChannelLayer = get_channel_layer()
    for member in conv.members.all():
        if member != user:
            async_to_sync(channel_layer.group_send)(
                member.username,
                {'type': 'notify', 'message': f'message has been read {user.username} {conv_id}'}
            )

    return request_success()

@require_POST
@CheckRequire
def delete_message(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    body = json.loads(req.body.decode('utf-8'))
    message_id = require(body, 'message', 'int', err_msg='Missing or error type of [message]')
    message = Message.objects.filter(id=message_id, notice=0).first()
    assert message is not None, ('[message] not found', 1, 404)
    assert user in message.conversation.members.all(), 'Bad param [message]'

    # insert the message into the deleted list of the user
    deleted_message = DeletedMessage.objects.get_or_create(user=user)[0]
    deleted_message.deleted.add(message)
    deleted_message.save()
    return request_success()

def format_conversation(conversation: Conversation) -> dict:
    return {
        'id': conversation.id,
        'type': conversation.type,
        'members': [user.username for user in conversation.members.all()]
    }

def format_group(group: Group) -> dict:
    return {
        'id': group.id,
        'name': group.name,
        'conversation': group.conversation.id,
        'master': group.master.username,
        'manager': [
            manager.username for manager in group.manager.all()
        ],
        'notice': [
            notice.id for notice in group.notice.all()
        ]
    }

def format_message(message: Message) -> dict:
    read = []
    for user in message.conversation.members.all():
        user_read = ReadMessage.objects.filter(conversation=message.conversation, user=user).first()
        if message.id > user_read.fro and message.id <= user_read.to:
            read.append(user.username)
    return {
        'id': message.id,
        'conversation': message.conversation.id,
        'sender': message.sender.username,
        'content': message.content,
        'timestamp': message.timestamp,
        'read': read,
        'reply_to': message.reply_to,
        'reply_by': message.reply_by
    }

@require_http_methods(['POST', 'GET'])
@CheckRequire
def group(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    if req.method == "POST":
        body = json.loads(req.body.decode('utf-8'))
        name = require(body, 'name', 'string', err_msg='Missing or error type of [name]')
        assert 0 < len(name) <= 40, 'Bad length of [name]'
        member_names = require(
            body, 'members', 'list[string]',
            err_msg='Missing or error type of [members]'
        )
        members = [user]
        for member_name in member_names:
            if member_name != user.username:
                friendship = Friend.objects.filter(
                    user=user, friend__username=member_name
                ).prefetch_related('friend').first()
                assert friendship is not None, 'Bad param [members]'
                members.append(friendship.friend)

        conversation = Conversation.objects.create(type=1)
        conversation.members.set(members)
        group = Group.objects.create(
            name=name, conversation=conversation, master=user
        )
        for member in members:
            ReadMessage.objects.get_or_create(
                conversation=conversation,
                user=member
            )
        return request_success({
            'group': format_group(group),
            'conversation': format_conversation(conversation)
        })

    else:
        group_id = req.GET.get('id')
        if group_id is None:
            group_list = []
            for group in Group.objects.all():
                if user in group.conversation.members.all():
                    group_list.append(format_group(group))
            return request_success({
                'groups': group_list
            })

        group_id = require({"id": group_id}, 'id', 'int', err_msg='Missing or error type of [id]')
        group = Group.objects.filter(id=group_id).first()
        if user not in group.conversation.members.all():
            return request_failed(1, 'Bad param [id]', 400)
        return request_success({
            'groups': [format_group(group),]
        })

@require_POST
@CheckRequire
def manager(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    body = json.loads(req.body.decode('utf-8'))
    group_id = require(body, 'group', 'int', err_msg='Missing or error type of [group]')
    group = Group.objects.filter(id=group_id).first()
    assert group is not None, 'Bad param [group]'
    assert user == group.master, 'Permission denied'

    add_names = require(
        body, 'add', 'list[string]',
        err_msg='Missing or error type of [add]'
    )
    add = []
    for add_name in add_names:
        new_manager = UserInfo.objects.filter(username=add_name).first()
        assert new_manager is not None, 'Bad param [add]'
        assert new_manager in group.conversation.members.all(), 'Bad param [add]'
        assert new_manager not in group.manager.all(), 'Bad param [add]'
        add.append(new_manager)

    delete_names = require(
        body, 'delete', 'list[string]',
        err_msg='Missing or error type of [delete]'
    )
    delete = []
    for delete_name in delete_names:
        delete_manager = UserInfo.objects.filter(username=delete_name).first()
        assert delete_manager is not None, 'Bad param [delete]'
        assert delete_manager in group.manager.all(), 'Bad param [delete]'
        delete.append(delete_manager)

    for manager in delete:
        group.manager.remove(manager)
    for manager in add:
        group.manager.add(manager)
    return request_success()

@require_POST
@CheckRequire
def master(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    body = json.loads(req.body.decode('utf-8'))
    group_id = require(body, 'group', 'int', err_msg='Missing or error type of [group]')
    group = Group.objects.filter(id=group_id).first()
    assert group is not None, 'Bad param [group]'
    assert user == group.master, 'Permission denied'
    master_name = require(body, 'master', 'string', err_msg='Missing or error type of [master]')
    master = UserInfo.objects.filter(username=master_name).first()
    assert master is not None, 'Bad param [master]'
    assert master in group.conversation.members.all(), 'Bad param [master]'

    group.master = master
    if master in group.manager.all():
        group.manager.remove(master)
    group.save()
    return request_success()

@require_POST
@CheckRequire
def remove_member(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    body = json.loads(req.body.decode('utf-8'))
    group_id = require(body, 'group', 'int', err_msg='Missing or error type of [group]')
    group = Group.objects.filter(id=group_id).first()
    assert group is not None, 'Bad param [group]'
    if user == group.master:
        flag = 0
    elif user in group.manager.all():
        flag = 1
    else:
        return request_failed(1, 'Permission denied')
    remove_names = require(
        body, 'remove', 'list[string]', err_msg='Missing or error type of [remove]'
    )
    remove: list[tuple[UserInfo, int]] = []
    for remove_name in remove_names:
        if remove_name == group.master.username:
            return request_failed(1, 'Permission denied')
        remove_member = UserInfo.objects.filter(username=remove_name).first()
        assert remove_member is not None, 'Bad param [remove]'
        assert remove_member in group.conversation.members.all(), 'Bad param [remove]'
        if remove_member in group.manager.all():
            if flag == 1:
                return request_failed(1, 'Permission denied')
            remove.append((remove_member, 1))
        else:
            remove.append((remove_member, 0))

    for member, is_manager in remove:
        group.conversation.members.remove(member)
        if is_manager == 1:
            group.manager.remove(member)
    group.conversation.save()
    group.save()

    channel_layer: InMemoryChannelLayer = get_channel_layer()
    for member, _ in remove:
        async_to_sync(channel_layer.group_send)(
            member.username,
            {'type': 'notify', 'message': f'removed from group {group_id}'}
        )
    return request_success()

@require_http_methods(['POST', 'GET'])
@CheckRequire
def group_notice(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    if req.method == "POST":
        body = json.loads(req.body.decode('utf-8'))
        group_id = require(body, 'group', 'int', err_msg='Missing or error type of [group]')
        group = Group.objects.filter(id=group_id).first()
        assert group is not None, 'Bad param [group]'
        assert user == group.master or user in group.manager.all(), 'Bad param [group]'

        content = require(
            body, 'content', 'string', err_msg='Missing or error type of [notice]'
        )
        notice = Message.objects.create(
            conversation=group.conversation, sender=user, content=content, notice=1
        )
        group.notice.add(notice)
        group.save()

        channel_layer: InMemoryChannelLayer = get_channel_layer()
        for member in group.conversation.members.all():
            if member != user:
                async_to_sync(channel_layer.group_send)(
                    member.username,
                    {'type': 'notify', 'message': f'new group notice in group {group_id}'}
                )
        return request_success({
            'notice': {
                'id': notice.id,
                'conversation': notice.conversation.id,
                'sender': user.username,
                'content': notice.content,
                'timestamp': notice.timestamp
            }
        })

    else:
        group_id = req.GET.get('group')
        group_id = require(
            {'id': group_id}, 'id', 'int', err_msg='Missing or error type of [group]'
        )
        group = Group.objects.filter(id=group_id).first()
        assert user in group.conversation.members.all(), 'Bad param [group]'

        notices = []
        for notice in group.notice.all():
            notices.append({
                'id': notice.id,
                'conversation': notice.conversation.id,
                'sender': notice.sender.username,
                'content': notice.content,
                'timestamp': notice.timestamp
            })
        return request_success({'notices': notices})

@require_POST
@CheckRequire
def invite(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    body = json.loads(req.body.decode('utf-8'))
    group_id = require(body, 'group', 'int', err_msg='Missing or error type of [group]')
    group = Group.objects.filter(id=group_id).first()
    assert user in group.conversation.members.all(), 'Bad param [group]'
    friendname = require(body, 'friend', 'string', err_msg='Missing or error type of [friend]')
    friendship = Friend.objects.filter(user=user, friend__username=friendname).first()
    assert friendship is not None, 'Bad param [friend]'
    friend = friendship.friend
    assert friend not in group.conversation.members.all(), 'Bad param [friend]'

    requests = Request.objects.filter(
        type=1, group=group, sender=friend
    )
    if len(requests) > 0:
        requests.delete()

    Request.objects.create(group=group, sender=friend, type=1)
    channel_layer: InMemoryChannelLayer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group.master.username,
        {'type': 'notify', 'message': f'new group request in group {group_id}'}
    )
    for member in group.manager.all():
        async_to_sync(channel_layer.group_send)(
            member.username,
            {'type': 'notify', 'message': f'new group request in group {group_id}'}
        )
    return request_success()

@require_GET
@CheckRequire
def group_request(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    group_id = req.GET.get('group')
    group_list = []
    if group_id is None:
        for group in Group.objects.all():
            if user == group.master or user in group.manager.all():
                group_list.append(group)

    else:
        group_id = require(
            {'group': group_id}, 'group', 'int', err_msg='Missing or error type of [group]'
        )
        group = Group.objects.filter(id=group_id).first()
        assert group is not None, 'Bad param [group]'
        group_list.append(group)
        assert user == group.master or user in group.manager.all(), 'Bad param [group]'

    requests = Request.objects.filter(type=1, group__in=group_list)
    request_list = []
    for request in requests:
        request_list.append({
            'group': request.group.id,
            'sender': request.sender.username,
            'nickname': request.sender.nickname,
            'email': request.sender.email,
            'status': request.status,
            'timestamp': request.timestamp
        })
    return request_success({
        'requests': request_list
    })

@require_POST
@CheckRequire
def process_group_request(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    body = json.loads(req.body.decode('utf-8'))
    group_id = require(body, 'group', 'int', err_msg='Missing or error type of [group]')
    group = Group.objects.filter(id=group_id).first()
    assert user == group.master or user in group.manager.all(), 'Bad param [group]'
    new_member = require(body, 'user', 'string', err_msg='Missing or error type of [user]')
    assert 0 < len(new_member) <= 16, 'Bad length of [user]'
    request = Request.objects.filter(type=1, group=group, sender__username=new_member).first()
    assert request is not None, ('Group request not found', 1, 404)
    assert request.status == 'Pending', 'Group request has been processed'
    decision = require(body, 'decision', 'string', err_msg='Missing or error type of [decision]')
    assert decision in ['Accept', 'Reject'], 'Bad param [decision]'
    if decision == 'Accept':
        group.conversation.members.add(request.sender)
        group.conversation.save()
        group.save()
        request.status = 'Accept'
        request.save()
        last_message = Message.objects.filter(
            conversation=group.conversation, notice=0
        ).order_by('id').last()
        if last_message is None:
            ReadMessage.objects.get_or_create(conversation=group.conversation, user=request.sender)
        else:
            read_message, _ = ReadMessage.objects.get_or_create(
                conversation=group.conversation, user=request.sender
            )
            read_message.fro=last_message.id
            read_message.to=last_message.id
            read_message.save()
        channel_layer: InMemoryChannelLayer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            request.sender.username,
            {'type': 'notify', 'message': f'new group added {group_id}'}
        )
    else:
        request.status = 'Reject'
        request.save()
    return request_success()

@require_POST
@CheckRequire
def leave_group(req: HttpRequest):
    jwt_token = req.headers.get("Authorization")
    jwt_token_payload = check_jwt_token(jwt_token)
    if jwt_token_payload is None:
        return request_failed(1, "Invalid or expired JWT", 401)
    user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
    assert user is not None, "USER NOT FOUND"

    body = json.loads(req.body.decode('utf-8'))
    group_id = require(body, 'group', 'int', err_msg='Missing or error type of [group]')
    group = Group.objects.filter(id=group_id).first()
    assert user in group.conversation.members.all(), 'Bad param [group]'
    assert user != group.master, 'New master should be set before leaving'
    group.conversation.members.remove(user)
    group.save()
    if user in group.manager.all():
        group.manager.remove(user)
    return request_success()
