import re
from datetime import datetime


class Bookmark:
    def __init__(self, title: str, url: str, time_created: datetime):
        self.title = title
        self.url = url
        self.time_created = time_created
        self.is_selected = False

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        self.__title = self._clean_title(value)

    @staticmethod
    def _clean_title(value: str):
        pattern = r'^(\(\d+\)\s).+'
        match = re.search(pattern, value)

        if match:
            redundant = match.group(1)
            value = value.split(redundant)[-1]

        value = value.split(' - YouTube')[0]

        return value
