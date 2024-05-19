import json
from django.test import TestCase
from chat.models import UserInfo, Friend


class UserAccountTests(TestCase):
    def test_register_user_success(self):
        # 测试用户成功注册
        url = str("/chat/register")  # 假设你的URL名称为'register'
        data = {
            "username": "testuser",
            "password": "a" * 64,  # 假设密码需要为64位
            "phone": "12345678901",
            "email": "test@example.com",
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserInfo.objects.filter(username="testuser").exists())

    def test_register_user_with_invalid_username(self):
        # 测试用户名无效（例如，长度超出范围）时的注册情况
        url = str("/chat/register")
        data = {
            "username": "u" * 17,  # 超出长度限制
            "password": "a" * 64,
            "phone": "12345678901",
            "email": "test@example.com",
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(UserInfo.objects.filter(email="test@example.com").exists())

    def test_login_success(self):
        # 假设已经有一个用户注册在数据库中
        UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        # 检查响应中是否包含token
        self.assertIn("token", response.json())

    def test_login_wrong_password(self):
        UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")
        data = {
            "username": "testuser",
            "password": "wrongpassword",
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        self.assertNotEqual(response.status_code, 200)

    def test_delete_account_success(self):

        UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        url = str("/chat/delete_account")  # 假设你的URL名称为'delete_account'
        data = {
            "password": "a" * 64,  # 假设密码需要为64位
        }
        header = {
            "HTTP_AUTHORIZATION": jwt,
        }
        response = self.client.delete(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(UserInfo.objects.filter(username="testuser").exists())

    def test_delete_account_wrong_password(self):
        UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]
        url = str("/chat/delete_account")
        # header = self.generate_header(user.username)
        data = {
            "password": "wrongpassword",
            # 'Authorization': token
        }
        header = {
            "HTTP_AUTHORIZATION": jwt,
        }
        response = self.client.delete(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertNotEqual(response.status_code, 200)

    def test_logout_success(self):
        UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]
        # print(jwt)

        url = str("/chat/logout")  # 假设你的URL名称为'logout'
        header = {
            "HTTP_AUTHORIZATION": jwt,
        }
        response = self.client.post(url, content_type="application/json", **header)
        self.assertEqual(response.status_code, 200)

    def test_logout_fail(self):
        UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        url = str("/chat/delete_account")  # 假设你的URL名称为'delete_account'
        data = {
            "password": "a" * 64,  # 假设密码需要为64位
        }
        header = {
            "HTTP_AUTHORIZATION": jwt,
        }
        response = self.client.delete(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(UserInfo.objects.filter(username="testuser").exists())

        url = str("/chat/logout")  # 假设你的URL名称为'logout'
        header = {
            "HTTP_AUTHORIZATION": jwt,
        }
        response = self.client.post(url, content_type="application/json", **header)
        self.assertEqual(response.status_code, 401)

    def test_find_usr(self):
        UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]
        self.assertEqual(response.status_code, 200)
        # 检查响应中是否包含token
        self.assertIn("token", response.json())

        url = "/chat/find_user/testuser"

        # Assume token generation and login have been handled
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.get(url, content_type="application/json", **header)
        self.assertEqual(response.status_code, 200)

        url = "/chat/find_user/next"

        # Assume token generation and login have been handled
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.get(url, content_type="application/json", **header)
        self.assertEqual(response.status_code, 404)

        url = "/chat/find_user/llllllllllllllllllllllllllllllllllllllllllll"

        # Assume token generation and login have been handled
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.get(url, content_type="application/json", **header)
        self.assertEqual(response.status_code, 400)

    def test_change_userinfo_success(self):
        UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]
        self.assertEqual(response.status_code, 200)
        # 检查响应中是否包含token
        self.assertIn("token", response.json())

        url = "/chat/change_userinfo"
        data = {
            "old_password": "a" * 64,
            "phone": "98765432101",
            "nickname": "lol",
            "password": "b" * 64,
            "email": "new_email@email.com",
            # "username": "newname",
        }
        # Assume token generation and login have been handled
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserInfo.objects.filter(phone="98765432101").exists())

        url = "/chat/change_userinfo"
        data = {
            "old_password": "b" * 64,
            "phone": "98765432101",
        }
        # Assume token generation and login have been handled
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 403)

        url = "/chat/change_userinfo"
        data = {
            "old_password": "a" * 64,
            "phone": "98765432101",
        }
        # Assume token generation and login have been handled
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 401)

        url = "/chat/change_userinfo"
        data = {
            "old_password": "b" * 64,
            "email": "new_email@email.com",
        }
        # Assume token generation and login have been handled
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 403)

        url = "/chat/change_userinfo"
        data = {
            "old_password": "b" * 64,
            "password": "fdgfhg",
        }
        # Assume token generation and login have been handled
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 400)

        url = "/chat/change_userinfo"
        data = {
            "old_password": "b" * 64,
            "nickname": "aa" * 14,
        }
        # Assume token generation and login have been handled
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 400)

        url = "/chat/change_userinfo"
        data = {
            "old_password": "b" * 64,
            "phone": "111" * 21,
        }
        # Assume token generation and login have been handled
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 400)

    def test_get_user_info_success(self):
        UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]
        self.assertEqual(response.status_code, 200)
        # 检查响应中是否包含token
        self.assertIn("token", response.json())

        url = "/chat/get_userinfo"
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.get(url, content_type="application/json", **header)
        self.assertEqual(response.status_code, 200)


class FriendTest(TestCase):
    def login(self):
        UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]
        self.assertEqual(response.status_code, 200)
        # 检查响应中是否包含token
        self.assertIn("token", response.json())
        return jwt

    def test_add_friend_success(self):
        jwt = self.login()

        UserInfo.objects.create(
            username="new_friend",
            password="a" * 64,
            phone="12345678903",
            email="newfriend@example.com",
        )
        url = "/chat/add_friend"
        data = {"friendname": "new_friend"}
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 200)

    def test_get_friend_list_success(self):
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/get_friend_list"
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.get(url, content_type="application/json", **header)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        # print(response_data)
        self.assertEqual(len(response_data["friends"]), 2)
        self.assertEqual(response_data["friends"][1]["username"], "friend1")

    def test_get_friend_request_success(self):
        UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        UserInfo.objects.create(
            username="new_friend",
            password="a" * 64,
            phone="12345678903",
            email="newfriend@example.com",
        )
        url = "/chat/add_friend"
        data = {"friendname": "new_friend"}
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 200)

        url = "/chat/get_friend_request"
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.get(url, content_type="application/json", **header)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        # print(response_data)
        self.assertEqual(len(response_data["friends"]), 1)
        self.assertEqual(response_data["friends"][0]["username"], "new_friend")

    def test_process_friend_request_success(self):
        # 登录testuser
        UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        # 向friend发请求
        UserInfo.objects.create(
            username="new_friend",
            password="a" * 64,
            phone="12345678903",
            email="newfriend@example.com",
        )
        url = "/chat/add_friend"
        data = {"friendname": "new_friend"}
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 200)

        # 退出testuser
        url = str("/chat/logout")  # 假设你的URL名称为'logout'
        header = {
            "HTTP_AUTHORIZATION": jwt,
        }
        response = self.client.post(url, content_type="application/json", **header)
        self.assertEqual(response.status_code, 200)

        # 登录friend
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "new_friend",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        # friend接受testuser请求
        url = "/chat/process_friend_request"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "friendname": "testuser",
            "decision": "Accept",
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 200)

        # 验证friend是否加上好友
        url = "/chat/get_friend_list"
        response = self.client.get(url, content_type="application/json", **header)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(len(response_data["friends"]), 1)
        self.assertEqual(response_data["friends"][0]["username"], "testuser")

        # 退出friend
        url = str("/chat/logout")  # 假设你的URL名称为'logout'
        header = {
            "HTTP_AUTHORIZATION": jwt,
        }
        response = self.client.post(url, content_type="application/json", **header)
        self.assertEqual(response.status_code, 200)

        # 登录testuser
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        # 验证testuser是否加上好友
        url = "/chat/get_friend_list"
        header = {
            "HTTP_AUTHORIZATION": jwt,
        }
        response = self.client.get(url, content_type="application/json", **header)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(len(response_data["friends"]), 1)
        self.assertEqual(response_data["friends"][0]["username"], "new_friend")

    def test_add_friend_tag(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        # hack加好友
        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )
        UserInfo.objects.create(
            username="friend2",
            password="a" * 64,
            phone="12345678905",
            email="newfriend2@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        # 加好友分组
        url = "/chat/add_friend_tag"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "friend_list": [
                "friend1",
            ],
            "tag": "best_friend",
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 200)

        url = "/chat/add_friend_tag"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "friend_list": [
                "friend2",
            ],
            "tag": "best_friend",
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 400)

        # 加好友分组
        url = "/chat/add_friend_tag"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "friend_list": [
                "friend0",
            ],
            "tag": "dsfdg" * 123,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 400)

    def test_get_friend_list_by_tag(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        # hack加好友
        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        # 加好友分组
        url = "/chat/add_friend_tag"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "friend_list": [
                "friend1",
            ],
            "tag": "best_friend",
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 200)

        # 获取分组 success
        url = "/chat/get_friend_list_by_tag/best_friend"
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.get(url, content_type="application/json", **header)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(len(response_data["friends"]), 1)
        self.assertEqual(response_data["friends"][0]["username"], "friend1")

        # 获取分组 fail
        url = "/chat/get_friend_list_by_tag/1111111111111111111111111111111111111"
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.get(url, content_type="application/json", **header)
        self.assertEqual(response.status_code, 400)

        # 获取分组 fail
        url = "/chat/get_friend_list_by_tag"
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.get(url, content_type="application/json", **header)
        self.assertEqual(response.status_code, 404)

    def test_delete_friend(self):
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/delete_friend"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {"friendname": "friend0"}
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 200)


class ChatTest(TestCase):
    def test_conversation_single(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/conversation"
        header = {"HTTP_AUTHORIZATION": jwt}
        # data = {"friendname": "friend0"}
        data = {
            "type": 0,
            "members": [
                "testuser",
                "friend0",
            ],
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 200)

    def test_conversation_group(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/conversation"
        header = {"HTTP_AUTHORIZATION": jwt}
        # data = {"friendname": "friend0"}
        data = {
            "type": 1,
            "members": [
                "testuser",
                "friend0",
                "friend1",
            ],
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 200)

    def test_get_conversation(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/conversation"
        header = {"HTTP_AUTHORIZATION": jwt}
        # data = {"friendname": "friend0"}
        data = {
            "type": 1,
            "members": [
                "testuser",
                "friend0",
                "friend1",
            ],
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )

        url = "/chat/conversation"

        response = self.client.get(url, content_type="application/json", **header)

        self.assertEqual(response.status_code, 200)

    def test_message(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/conversation"
        header = {"HTTP_AUTHORIZATION": jwt}
        # data = {"friendname": "friend0"}
        data = {
            "type": 1,
            "members": [
                "testuser",
                "friend0",
                "friend1",
            ],
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        # print(response.json())
        cid = response.json()["conversation"]["id"]

        data = {"conversation": cid, "content": "This is a text.", "reply_to": -1}

        url = "/chat/message"
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 200)

    def test_get_message(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/conversation"
        header = {"HTTP_AUTHORIZATION": jwt}
        # data = {"friendname": "friend0"}
        data = {
            "type": 1,
            "members": [
                "testuser",
                "friend0",
                "friend1",
            ],
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        idx = response.json()["conversation"]["id"]

        url = "/chat/message"
        for i in range(5):
            data = {
                "conversation": idx,
                "content": "This is a text" + str(i),
                "reply_to": -1,
            }
            response = self.client.post(
                url, json.dumps(data), content_type="application/json", **header
            )
        url = "/chat/message?conversation=" + str(idx) + "&after=2"
        response = self.client.get(url, content_type="application/json", **header)

        self.assertEqual(response.status_code, 200)

    def test_read_conversation(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/conversation"
        header = {"HTTP_AUTHORIZATION": jwt}
        # data = {"friendname": "friend0"}
        data = {
            "type": 1,
            "members": [
                "testuser",
                "friend0",
                "friend1",
            ],
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        idx = response.json()["conversation"]["id"]

        url = "/chat/message"
        for i in range(5):
            data = {
                "conversation": idx,
                "content": "This is a text" + str(i),
                "reply_to": -1,
            }
            response = self.client.post(
                url, json.dumps(data), content_type="application/json", **header
            )
        url = "/chat/read_conversation"
        data = {"conversation": idx}
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_conversation(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/conversation"
        header = {"HTTP_AUTHORIZATION": jwt}
        # data = {"friendname": "friend0"}
        data = {
            "type": 1,
            "members": [
                "testuser",
                "friend0",
                "friend1",
            ],
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        idx = response.json()["conversation"]["id"]

        url = "/chat/message"
        for i in range(5):
            data = {
                "conversation": idx,
                "content": "This is a text" + str(i),
                "reply_to": -1,
            }
            response = self.client.post(
                url, json.dumps(data), content_type="application/json", **header
            )
        url = "/chat/delete_message"
        data = {"message": 2}
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        self.assertEqual(response.status_code, 200)

class GroupTest(TestCase):
    def test_group(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/group"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "name": "capybala",
            "members": ["friend0", "friend1"]
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        idx = response.json()["group"]["id"]

        self.assertEqual(response.status_code, 200)

        url = "/chat/group?id="+ str(idx)
        header = {"HTTP_AUTHORIZATION": jwt}

        response = self.client.get(
            url, content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 200)

    def test_manager(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/group"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "name": "capybala",
            "members": ["friend0", "friend1"]
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        idx = response.json()["group"]["id"]

        self.assertEqual(response.status_code, 200)

        url = "/chat/manager"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "group": idx,
            "add": ["friend1", "friend0"], 
            "delete": [] 
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 200)

        url = "/chat/manager"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "group": idx,
            "add": [], 
            "delete": ["friend0", "friend1"], 
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 200)

    def test_master(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/group"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "name": "capybala",
            "members": ["friend0", "friend1"]
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        idx = response.json()["group"]["id"]

        self.assertEqual(response.status_code, 200)

        url = "/chat/master"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "group": idx,
            "master": "friend1"
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 200)

    def test_remove_member(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/group"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "name": "capybala",
            "members": ["friend0", "friend1"]
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        idx = response.json()["group"]["id"]

        self.assertEqual(response.status_code, 200)

        url = "/chat/remove_member"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "group": idx,
            "remove": ["friend0"]
        }


        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 200)

    def test_group_notice(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/group"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "name": "capybala",
            "members": ["friend0", "friend1"]
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        idx = response.json()["group"]["id"]

        self.assertEqual(response.status_code, 200)

        url = "/chat/group_notice"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "group": idx,
            "content": "This is a notice."
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 200)

        url = "/chat/group_notice?group=" + str(idx)
        header = {"HTTP_AUTHORIZATION": jwt}
        response = self.client.get(
            url, content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 200)

    def test_invite(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/group"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "name": "capybala",
            "members": ["friend0"]
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        idx = response.json()["group"]["id"]

        self.assertEqual(response.status_code, 200)

        url = "/chat/invite"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "group": idx,
            "friend": "friend1"
        }


        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 200)

    def test_group_request(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/group"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "name": "capybala",
            "members": ["friend0"]
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        idx = response.json()["group"]["id"]

        self.assertEqual(response.status_code, 200)

        url = "/chat/invite"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "group": idx,
            "friend": "friend1"
        }


        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 200)

        url = "/chat/group_request?group=" + str(idx)
        header = {"HTTP_AUTHORIZATION": jwt}

        response = self.client.get(
            url,content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 200)

    def test_process_group_request(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/group"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "name": "capybala",
            "members": ["friend0"]
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        idx = response.json()["group"]["id"]

        self.assertEqual(response.status_code, 200)

        url = "/chat/invite"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "group": idx,
            "friend": "friend1"
        }


        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 200)

        url = "/chat/process_group_request"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "group": idx,
            "user": "friend1",
            "decision": "Accept" 
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 200)

    def test_leave_group(self):
        # 登录testuser
        testuser = UserInfo.objects.create(
            username="testuser",
            password="a" * 64,
            phone="12345678901",
            email="test@example.com",
        )
        url = str("/chat/login")  # 假设你的URL名称为'login'
        data = {
            "username": "testuser",
            "password": "a" * 64,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        jwt = response.json()["token"]

        friend0 = UserInfo.objects.create(
            username="friend0",
            password="a" * 64,
            phone="12345678903",
            email="newfriend0@example.com",
        )
        friend1 = UserInfo.objects.create(
            username="friend1",
            password="a" * 64,
            phone="12345678904",
            email="newfriend1@example.com",
        )

        Friend.objects.create(user=testuser, friend=friend0)
        Friend.objects.create(user=friend0, friend=testuser)
        Friend.objects.create(user=testuser, friend=friend1)
        Friend.objects.create(user=friend1, friend=testuser)

        url = "/chat/group"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "name": "capybala",
            "members": ["friend0"]
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )
        idx = response.json()["group"]["id"]

        self.assertEqual(response.status_code, 200)

        url = "/chat/master"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "group": idx,
            "master": "friend0"
        }

        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 200)

        url = "/chat/leave_group"
        header = {"HTTP_AUTHORIZATION": jwt}
        data = {
            "group": idx,
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 200)
