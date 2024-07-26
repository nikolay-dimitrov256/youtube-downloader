import sqlite3
import os
import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List

from bookmark import Bookmark


class BookmarkLoader(ABC):
    def __init__(self):
        self.path_to_bookmarks = ''

    @abstractmethod
    def load_bookmarks(self, search: str = '', ascending=False, limit: int = None) -> List[Bookmark]:
        pass


class FirefoxLoader(BookmarkLoader):

    def load_bookmarks(self, search: str = '', ascending=False, limit: int = None) -> List[Bookmark]:
        firefox_profile_dir = os.path.expanduser(self.path_to_bookmarks)
        # Path to the bookmarks SQLite database file
        bookmarks_db_path = os.path.join(firefox_profile_dir, 'places.sqlite')

        # Connect to the SQLite database
        connection = sqlite3.connect(bookmarks_db_path)
        cursor = connection.cursor()

        # Query the bookmarks
        query = self._get_query(search, ascending, limit)
        cursor.execute(query)
        bookmarks_data = cursor.fetchall()

        bookmarks = [Bookmark(title, url, self._convert_date(date_added)) for title, url, date_added in bookmarks_data]

        connection.close()

        return bookmarks

    @staticmethod
    def _convert_date(epoch_time) -> datetime:
        return datetime(1970, 1, 1) + timedelta(microseconds=epoch_time)

    @staticmethod
    def _get_query(search: str, ascending: bool, limit: int):
        query = f"""
        SELECT
            mb.title,
            mp.url,
            mb.dateAdded
        FROM
            moz_bookmarks AS mb
        JOIN
            moz_places AS mp
        ON 
            mb.fk = mp.id
        WHERE
            LOWER(mp.url) LIKE '%youtube.com%'
            {f'AND LOWER(mb.title) LIKE %{search}%' if search else ''}
        ORDER BY
            mb.dateAdded {'ASC' if ascending else 'DESC'}
        {f'LIMIT {limit}' if limit else ''}
        """

        return query


class ChromeLoader(BookmarkLoader):

    def load_bookmarks(self, search: str = '', ascending=False, limit: int = None) -> List[Bookmark]:
        self.path_to_bookmarks = os.path.join(self.path_to_bookmarks, 'Bookmarks')

        with open(self.path_to_bookmarks, encoding='utf-8') as file:
            data = json.load(file)

        bookmarks = []
        bookmarks = self._walk_json(bookmarks, data['roots'], search)
        bookmarks = sorted(bookmarks, key=lambda x: x.time_created, reverse=not ascending)

        if limit:
            bookmarks = bookmarks[:limit]

        return bookmarks

    @staticmethod
    def _convert_date(chrome_time) -> datetime:
        return datetime(1601, 1, 1) + timedelta(microseconds=chrome_time)

    def _walk_json(self, bookmarks: List[Bookmark], dictionary: dict, search: str) -> List[Bookmark]:
        for key, value in dictionary.items():
            if key in ['bookmark_bar', 'other', 'synced']:
                bookmarks = self._walk_json(bookmarks, value, search)

            elif key == 'children':
                for child in value:
                    if child['type'] == 'folder':
                        bookmarks = self._walk_json(bookmarks, child, search)
                    elif child['type'] == 'url':
                        title = child['name']
                        url = child['url']
                        time_created = int(child['date_added'])
                        time_created = self._convert_date(time_created)

                        if 'youtube.com' not in url.lower():
                            continue

                        if search not in title:
                            continue

                        bookmark = Bookmark(title, url, time_created)
                        bookmarks.append(bookmark)

        return bookmarks

# loader = ChromeLoader()
# loader.path_to_bookmarks = 'C:\\Users\\NIKOLAY\\AppData\\Local\\Google\\Chrome\\User Data\\Default'
#
# bookmarks = loader.load_bookmarks()
#
# for b in bookmarks:
#     print(b.title)
