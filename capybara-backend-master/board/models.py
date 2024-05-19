# pylint: disable=C0103
"""
The data models of the board module.
"""

from django.db import models

from utils import utils_time
from utils.utils_request import return_field
from utils.utils_require import MAX_CHAR_LENGTH, STATE_LENGTH

# Create your models here.

class User(models.Model):
    """
    The user model.
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=MAX_CHAR_LENGTH, unique=True)
    password = models.CharField(max_length=MAX_CHAR_LENGTH)
    created_time = models.FloatField(default=utils_time.get_timestamp)

    class Meta:
        """
        The meta data of the user model.
        """
        indexes = [models.Index(fields=["name"])]

    def serialize(self):
        """
        The serialization method of the user model.
        """
        boards = Board.objects.filter(user=self)
        return {
            "id": self.id, 
            "name": self.name, 
            "createdAt": self.created_time,
            "boards": [
                return_field(board.serialize(), [
                    "id", "boardName", "userName", "createdAt"
                ]) for board in boards
            ]
        }

    def __str__(self) -> str:
        return self.name


class Board(models.Model):
    """
    The board model.
    """
    # id, BigAutoField, primary_key=True
    id = models.BigAutoField(primary_key=True)
    # user, ForeignKey to User, CASCADE deletion
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # board_state, CharField
    board_state = models.TextField(max_length=STATE_LENGTH)
    # board_name, CharField
    board_name = models.CharField(max_length=MAX_CHAR_LENGTH)
    # created_time, FloatField, default=utils_time.get_timestamp
    created_time = models.FloatField(default=utils_time.get_timestamp)

    # Meta data
    class Meta:
        """
        The meta data of the board model.
        """
        # Create index on board_name
        indexes = [models.Index(fields=["board_name"])]
        # Create unique_together on user and board_name
        unique_together = ["user", "board_name"]

    def serialize(self):
        """
        The serialization method of the board model.
        """
        userName = self.user.name
        return {
            "id": self.id,
            "board": self.board_state, 
            "boardName": self.board_name,
            "userName": userName,
            "createdAt": self.created_time
        }

    def __str__(self) -> str:
        return f"{self.user.name}'s board {self.board_name}"
