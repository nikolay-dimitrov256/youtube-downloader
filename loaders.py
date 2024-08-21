import sqlite3
import os
import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Tuple

from bookmark import Bookmark


class BookmarkLoader(ABC):
    def __init__(self):
        # The path to the directory where the bookmarks file is located.
        self.path_to_bookmarks = ''

    @abstractmethod
    def load_bookmarks(self, search: str = '', ascending=False, limit: int = None) -> List[Bookmark]:
        """
        :param search: string, optional. If it is filled, only the bookmarks, which contain the string case
        insensitively are returned, else all bookmarks are returned.
        :param ascending: boolean, optional. Sets the ordering of the bookmarks by creation date.
        :param limit: integer, optional. Sets the number of bookmarks returned. If it is not filled, all bookmarks are
        returned.
        :return: list of Bookmark objects
        """

        pass


class FirefoxLoader(BookmarkLoader):

    def load_bookmarks(self, search: str = '', ascending=False, limit: int = None) -> List[Bookmark]:
        """
        :param search: string, optional. If it is filled, only the bookmarks, which contain the string case
        insensitively are returned, else all bookmarks are returned.
        :param ascending: boolean, optional. Sets the ordering of the bookmarks by creation date.
        :param limit: integer, optional. Sets the number of bookmarks returned. If it is not filled, all bookmarks are
        returned.
        :return: list of Bookmark objects
        """

        firefox_profile_dir = os.path.expanduser(self.path_to_bookmarks)
        # Path to the bookmarks SQLite database file
        bookmarks_db_path = os.path.join(firefox_profile_dir, 'places.sqlite')

        # Connect to the SQLite database
        connection = sqlite3.connect(bookmarks_db_path)
        cursor = connection.cursor()

        # Query the bookmarks
        query, params = self._get_query(search, ascending, limit)
        cursor.execute(query, params)
        bookmarks_data = cursor.fetchall()

        # Load the bookmarks as list of Bookmark objects
        bookmarks = [Bookmark(title, url, self._convert_date(date_added)) for title, url, date_added in bookmarks_data]

        connection.close()

        return bookmarks

    @staticmethod
    def _convert_date(epoch_time: int) -> datetime:
        """
        :param epoch_time: int. The time since 1970.01.01 in microseconds as taken from the Firefox bookmarks
        :return: datetime. The date and time of the creation of the bookmark
        """
        return datetime(1970, 1, 1) + timedelta(microseconds=epoch_time)

    @staticmethod
    def _get_query(search: str, ascending: bool, limit: int) -> Tuple[str, tuple]:
        # Prepare the search pattern with wildcards
        search_pattern = f'%{search.lower()}%' if search else '%'

        # Create the base query
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
            AND LOWER(mb.title) LIKE ?
        ORDER BY
            mb.dateAdded {'ASC' if ascending else 'DESC'}
        {f'LIMIT {limit}' if limit else ''}
        ;
        """

        return query, (search_pattern,)

    def __str__(self):
        return 'Mozilla Firefox'


class ChromeLoader(BookmarkLoader):

    def load_bookmarks(self, search: str = '', ascending=False, limit: int = None) -> List[Bookmark]:
        """
        :param search: string, optional. If it is filled, only the bookmarks, which contain the string case
        insensitively are returned, else all bookmarks are returned.
        :param ascending: boolean, optional. Sets the ordering of the bookmarks by creation date.
        :param limit: integer, optional. Sets the number of bookmarks returned. If it is not filled, all bookmarks are
        returned.
        :return: list of Bookmark objects
        """

        # The path to the bookmarks file
        path_to_bookmarks = os.path.join(self.path_to_bookmarks, 'Bookmarks')

        # Load the bookmarks data as a dictionary
        with open(path_to_bookmarks, encoding='utf-8') as file:
            data = json.load(file)

        bookmarks = []

        # Extract the bookmarks from the dictionary as a list of Bookmark objects
        bookmarks = self._walk_json(bookmarks, data['roots'], search)

        # Sort the bookmarks by time created
        bookmarks = sorted(bookmarks, key=lambda x: x.time_created, reverse=not ascending)

        # Apply the limit if there is such
        if limit:
            bookmarks = bookmarks[:limit]

        return bookmarks

    @staticmethod
    def _convert_date(chrome_time) -> datetime:
        """
        :param chrome_time: int. The time since 1601.01.01 in microseconds as taken from the Chrome bookmarks
        :return: datetime. The date and time of the creation of the bookmark
        """

        return datetime(1601, 1, 1) + timedelta(microseconds=chrome_time)

    def _walk_json(self, bookmarks: List[Bookmark], dictionary: dict, search: str) -> List[Bookmark]:
        """
        :param bookmarks: List of Bookmark objects. Empty
        :param dictionary: dict. All bookmarks and folders in the Chrome bookmarks
        :param search: str. Search by a keyword. If not filled, all YouTube bookmarks are returned
        :return: list of Bookmark objects
        """
        # Iterate through the data
        for key, value in dictionary.items():
            if key in ['bookmark_bar', 'other', 'synced']:  # The three main folders in the Chrome bookmarks
                bookmarks = self._walk_json(bookmarks, value, search)

            elif key == 'children':  # If it is a list, iterate through its elements
                for child in value:
                    if child['type'] == 'folder':  # If the child is a folder, call the method recursively
                        bookmarks = self._walk_json(bookmarks, child, search)
                    elif child['type'] == 'url':  # If the child is an url, take its data
                        title = child['name']
                        url = child['url']
                        time_created = int(child['date_added'])
                        time_created = self._convert_date(time_created)

                        if 'youtube.com' not in url.lower():  # If the bookmark does not lead to YouTube
                            continue

                        # Case insensitively search for a keyword. Allways true if the keyword is an empty string
                        if search.lower() not in title.lower():
                            continue

                        # Create the Bookmark object and append it to the list
                        bookmark = Bookmark(title, url, time_created)
                        bookmarks.append(bookmark)

        return bookmarks

    def __str__(self):
        return 'Google Chrome'


# Test code
if __name__ == '__main__':
    loader = FirefoxLoader()
    loader.path_to_bookmarks = 'C:/Users/NIKOLAY/AppData/Roaming/Mozilla/Firefox/Profiles/tarigwgs.default-release'

    bookmarks_ = loader.load_bookmarks()

    for b in bookmarks_:
        print(b.title)
