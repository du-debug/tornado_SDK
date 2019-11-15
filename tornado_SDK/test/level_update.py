"""
Level_Update
"""
from .app_mixin import AppMixin


class LevelUpdate(AppMixin):

    keys = ('name', 'age')

    def __init__(self):
        pass

    def process(self, request_handler, params):
        request_handler.write('level_update success')
        request_handler.finish()
        return True

    def get_params_keys(self):
        return LevelUpdate.keys

