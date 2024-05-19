# pylint: disable=W0613, C0103
import json
from typing import Any
from django.http import HttpRequest, HttpResponse

from board.models import Board, User
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import STATE_LENGTH, CheckRequire, require
from utils.utils_jwt import generate_jwt_token, check_jwt_token


@CheckRequire
def startup(req: HttpRequest):
    return HttpResponse(
        "Congratulations! You have successfully installed the requirements. Go ahead!"
    )


@CheckRequire
def login(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD

    # Request body example: {"userName": "Ashitemaru", "password": "123456"}
    body = json.loads(req.body.decode("utf-8"))

    username = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    password = require(body, "password", "string", err_msg="Missing or error type of [password]")

    # If the user does not exist, create a new user and save;
    # while if the user exists, check the password
    user = User.objects.filter(name=username).first()
    # If new user or checking success,
    # return code 0, "Succeed", with {"token": generate_jwt_token(user_name)}
    if user is None:
        user = User.objects.create(name=username, password=password)
        return request_success({"token": generate_jwt_token(username)})

    if user.password == password:
        return request_success({"token": generate_jwt_token(username)})

    # Else return request_failed with code 2, "Wrong password", http status code 401
    return request_failed(2, "Wrong password", 401)

    # return request_failed(1, "Not implemented", 501)


def check_for_board_data(body):
    board = require(body, "board", "string", err_msg="Missing or error type of [board]")
    board_name = require(
        body, "boardName", "string", err_msg="Missing or error type of [boardName]"
    )
    user_name = require(
        body, "userName", "string", err_msg="Missing or error type of [userName]"
    )

    assert 0 < len(board_name) <= 50, "Bad length of [boardName]"
    assert 0 < len(user_name) <= 50, "Bad length of [userName]"
    assert len(board) == STATE_LENGTH, "Bad length of [board]"
    assert all([c in ('0', '1') for c in board]), "Invalid char in [board]" # pylint: disable=R1729

    return board, board_name, user_name


@CheckRequire
def boards(req: HttpRequest):
    if req.method == "GET":
        board_list = Board.objects.all().order_by('-created_time')
        return_data = {
            "boards": [
                # Only provide required fields to lower the latency of
                # transmitting LARGE packets through unstable network
                return_field(board.serialize(), ["id", "boardName", "createdAt", "userName"])
            for board in board_list],
        }
        return request_success(return_data)

    if req.method == "POST":
        jwt_token = req.headers.get("Authorization")
        body = json.loads(req.body.decode("utf-8"))

        # First check jwt_token.
        # If not exists, return code 2, "Invalid or expired JWT", http status code 401
        jwt_token_payload = check_jwt_token(jwt_token)
        if jwt_token_payload is None:
            return request_failed(2, "Invalid or expired JWT", 401)

        # Then invoke `check_for_board_data` to check the body data
        # and get the board_state, board_name and user_name.
        # Check the user_name with the username in jwt_token_payload.
        # If not match, return code 3, "Permission denied", http status code 403
        board_state, board_name, user_name = check_for_board_data(body)
        if user_name != jwt_token_payload["username"]:
            return request_failed(3, "Permission denied", 403)

        # Find the corresponding user instance by user_name. We can assure that the user exists.
        user = User.objects.filter(name=user_name).first()

        # We lookup if the board with the same name and the same user exists.
        ## If not exists, new an instance of Board type, then save it to the database.
        ## If exists, change corresponding value of current `board`, then save it to the database.
        board = Board.objects.filter(user=user, board_name=board_name).first()
        if board is None:
            board = Board.objects.create(user=user, board_state=board_state, board_name=board_name)
            board.save()
            return request_success({"isCreate": True})

        board.board_state = board_state
        board.save()
        return request_success({"isCreate": False})

    return BAD_METHOD


@CheckRequire
def boards_index(req: HttpRequest, index: Any): # pylint: disable=R0911

    idx = require({"index": index}, "index", "int", err_msg="Bad param [id]", err_code=-1)
    assert idx >= 0, ("Bad param [id]", -1)

    if req.method == "GET":
        board = Board.objects.filter(id=idx).first()  # Return None if not exists

        if board:
            return request_success(
                return_field(board.serialize(), ["board", "boardName", "userName"])
            )

        return request_failed(1, "Board not found", status_code=404)

    if req.method == "DELETE":
        jwt_token = req.headers.get("Authorization")
        jwt_token_payload = check_jwt_token(jwt_token)
        if jwt_token_payload is None:
            return request_failed(2, "Invalid or expired JWT", 401)

        board = Board.objects.filter(id=idx).first()
        if board:
            if jwt_token_payload["username"] != board.user.name:
                return request_failed(3, "Cannot delete board of other users", 403)

            board.delete()
            return request_success()

        return request_failed(1, "Board not found", status_code=404)

    return BAD_METHOD


@CheckRequire
def user_board(req: HttpRequest, userName: Any):
    name = require(
        {"userName": userName},
        "userName", "string", err_msg="Bad param [userName]", err_code=-1
    )

    assert 0 < len(name) <= 50, ("Bad param [userName]", -1)

    if req.method == "GET":
        user = User.objects.filter(name=name).first()
        if user is None:
            return request_failed(1, "User not found", status_code=404)

        board_list = Board.objects.filter(user=user).order_by('-created_time')
        return request_success({
            "userName": name,
            "boards": [
                return_field(
                    board.serialize(),
                    ["id", "boardName", "createdAt", "userName"]
                ) for board in board_list
            ]
        })

    return BAD_METHOD
