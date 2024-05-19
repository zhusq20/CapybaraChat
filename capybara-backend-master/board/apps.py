"""
The config of the board module.
"""

from django.apps import AppConfig


class BoardConfig(AppConfig):
    """
    The config class for the board module.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'board'
