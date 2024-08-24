import json
import yt_dlp
import tkinter as tk
from tkinter import ttk, filedialog
from typing import Optional, List

from bookmark import Bookmark
from loaders import BookmarkLoader, FirefoxLoader, ChromeLoader
from scrollable_frame import ScrollableFrame


class YoutubeDownloader:
    supported_browsers = {
        'Mozilla Firefox': FirefoxLoader,
        'Google Chrome': ChromeLoader,
    }

    def __init__(self):
        self.settings = self.load_settings()
        self.loader: Optional[BookmarkLoader] = None
        self.bookmarks: List[Bookmark] = []
        self.bookmarks_state: List[tk.BooleanVar] = []
        self.root = tk.Tk()
        self.root.title('Youtube Downloader')

        self.render_widgets()

    @property
    def loader(self):
        return self.__loader

    @loader.setter
    def loader(self, value: BookmarkLoader):
        if value is not None:
            value.path_to_bookmarks = self.settings.get(str(value))
        self.__loader = value

    @staticmethod
    def load_settings():
        try:
            with open('settings.txt') as file:
                # Parse the JSON data as dictionary
                settings = json.loads(file.read())

                return settings
        except FileNotFoundError:
            return {}

    def save_settings(self):
        with open('settings.txt', 'w') as file:
            # Write the dictionary as JSON
            file.write(json.dumps(self.settings))

    def render_widgets(self):
        main_tab = ttk.Notebook(self.root)
        main_frame = ttk.Frame(main_tab)
        settings_frame = ttk.Frame(main_tab)
        main_tab.add(main_frame, text='Downloader')
        main_tab.add(settings_frame, text='Settings')
        main_tab.pack()

        self.render_download_tab(main_frame)

        self.render_settings_tab(settings_frame)

    def render_download_tab(self, main_frame: ttk.Frame):
        download_frame = ttk.LabelFrame(main_frame, text='Download from single URL')
        download_frame.grid(row=0, column=0)

        url_frame = ttk.LabelFrame(download_frame, text='Enter URL:')
        url_frame.grid(row=2, columnspan=2, pady=(0, 10))

        url_entry = ttk.Entry(url_frame, width=70)
        url_entry.bind('<FocusIn>', lambda e: url_entry.delete(0, tk.END))
        url_entry.pack()

        message_frame = ttk.Frame(download_frame)
        message_frame.grid(row=7, columnspan=2)
        message_scroll = ttk.Scrollbar(message_frame)
        message_scroll.pack(side='right', fill='y')

        message_field = tk.Text(message_frame, width=50, height=24, yscrollcommand=message_scroll.set)
        message_field.pack()
        message_scroll.config(command=message_field.yview)

        ttk.Button(
            download_frame,
            text='Download mp3',
            command=lambda: self.download_mp3(url_entry.get(), message_field)
        ).grid(row=4, column=0)
        ttk.Button(
            download_frame,
            text='Download video',
            command=lambda: self.download_video(url_entry.get(), message_field)
        ).grid(row=4, column=1)

        ttk.Separator(download_frame).grid(row=6, columnspan=2, pady=10, sticky='we')

        bookmarks_frame = ttk.Labelframe(main_frame, text='Load bookmarks from browser')
        bookmarks_frame.grid(row=0, column=1, sticky='n', padx=5)

        ttk.Label(bookmarks_frame, text='Chose a browser: ').grid(row=1, column=0, sticky='w')
        current_browser = tk.StringVar()
        select_browser_dropdown = ttk.Combobox(
            bookmarks_frame,
            textvariable=current_browser,
            width=30,
            values=list(self.supported_browsers.keys())
        )
        select_browser_dropdown.grid(row=1, column=1, pady=5, sticky='w')

        ttk.Label(bookmarks_frame, text='Search: ').grid(row=2, column=0, sticky='w')
        search_field = ttk.Entry(bookmarks_frame, width=33)
        search_field.grid(row=2, column=1, sticky='w', pady=5)

        ascending = tk.BooleanVar()
        ascending_checkbutton = ttk.Checkbutton(
            bookmarks_frame,
            text='Order bookmarks from older to newer',
            variable=ascending,
        )
        ascending_checkbutton.grid(row=3, column=0, pady=5, sticky='w')

        ttk.Label(bookmarks_frame, text='Number of bookmarks: ').grid(row=5, column=0, sticky='w')
        number_entry = ttk.Entry(bookmarks_frame, width=5)
        number_entry.grid(row=5, column=1, sticky='w', pady=5)

        loaded_bookmarks_frame = ScrollableFrame(bookmarks_frame)
        loaded_bookmarks_frame.grid(row=9, columnspan=2, sticky='nsew')

        ttk.Button(
            bookmarks_frame,
            text='Load Bookmarks',
            command=lambda: self.load_bookmarks(
                message_field,
                current_browser.get(),
                search_field.get(),
                ascending.get(),
                number_entry.get(),
                loaded_bookmarks_frame,
                bookmarks_frame
            ),
        ).grid(row=7, column=1, sticky='e', pady=5)

        ttk.Separator(bookmarks_frame).grid(row=8, columnspan=2, sticky='we', pady=5)

    def render_settings_tab(self, settings_frame: ttk.Frame):
        ttk.Label(settings_frame, text='Chose a browser: ').grid(row=2, column=0, padx=5, pady=5, sticky='w')
        current_browser = tk.StringVar()
        select_browser_dropdown = ttk.Combobox(
            settings_frame,
            textvariable=current_browser,
            width=30,
            values=list(self.supported_browsers.keys())
        )
        select_browser_dropdown.grid(row=2, column=1, pady=5, sticky='w')

        ttk.Button(
            settings_frame,
            text='Select Path',
            command=lambda: self.select_path_to_bookmarks(current_browser.get()),
        ).grid(row=4, column=1, sticky='w')

        ttk.Button(
            settings_frame,
            text='Save',
            command=self.save_settings
        ).grid(row=6, column=1, pady=30)

    def select_path_to_bookmarks(self, browser: str):
        # If the user didn't select a supported browser, do nothing
        if not browser or browser not in self.supported_browsers:
            return

        # Open file dialog so the user selects the path to the directory, containing the bookmarks file
        path = filedialog.askdirectory()

        # If the user pressed 'Cancel', do nothing
        if not path:
            return

        # Set the path in the settings dictionary
        self.settings[browser] = path

    def load_bookmarks(self, textbox: tk.Text, selected_browser, search, ascending, limit,
                       parent_frame: ScrollableFrame, grandparent_frame: ttk.LabelFrame):
        # Get a reference to the relevant inheritor of the BookmarkLoader class
        loader = self.supported_browsers.get(selected_browser)

        # If the user didn't select a supported browser, output a message and do nothing
        if not loader:
            self.output_message(textbox, 'Please select a supported browser')
            return

        # Set up an instance of the inheritor of the BookmarkLoader class
        self.loader = loader()

        # Try to set the limit argument, if the user filled in a number
        try:
            limit = int(limit)
        except ValueError:
            limit = None

        # Try to load the relevant browser's bookmarks, if the user has selected the correct path to the bookmarks file
        try:
            self.bookmarks = self.loader.load_bookmarks(search, ascending, limit)

            self.render_bookmarks(parent_frame, grandparent_frame, textbox)
        except Exception as e:
            # If an error is raised, output the error's message
            self.output_message(textbox, str(e))

    def render_bookmarks(self, parent_frame: ScrollableFrame, grand_parent_frame: ttk.LabelFrame, textbox: tk.Text):
        # Clear the rendered bookmarks
        self.clear_frame(parent_frame.scrollable_frame)

        # For every bookmark, render it in the scrollable frame
        for index, bookmark in enumerate(self.bookmarks):
            self.render_single_bookmark(parent_frame.scrollable_frame, index, bookmark)

        # After all bookmarks are rendered, render the footer buttons
        self.render_footer_buttons(grand_parent_frame, textbox)

    def render_single_bookmark(self, parent: tk.Frame, row, bookmark: Bookmark) -> None:
        # Set up a tk.Frame, and put it in the parent Frame
        bookmark_frame = tk.Frame(parent)
        bookmark_frame.grid(row=row, column=0, sticky='we')

        # Set up a tk.BooleanVar, representing the is_selected state of the *rendered* bookmark,
        # and append it to an instance collection
        is_selected = tk.BooleanVar()
        self.bookmarks_state.append(is_selected)

        # Render a ttk.Checkbutton, allowing the user to select and unselect the corresponding bookmark
        selected_checkbutton = ttk.Checkbutton(
            bookmark_frame,
            variable=is_selected,
            command=lambda: self.select_bookmark(bookmark, is_selected.get()),
        )
        selected_checkbutton.grid(row=0, column=0, sticky='w')

        # Render a Label with the bookmark's title as text
        ttk.Label(bookmark_frame, text=bookmark.title).grid(row=0, column=1, sticky='we')

    def render_footer_buttons(self, grand_parent_frame: ttk.LabelFrame, textbox: tk.Text):
        # Create a Frame to contain the footer buttons and put it at the bottom of the bookmarks LabelFrame
        button_frame = tk.Frame(grand_parent_frame)
        button_frame.grid(row=11, columnspan=2, pady=(5, 0), sticky='nsew')

        # Create a Button to select all bookmarks
        ttk.Button(
            button_frame,
            text='Select all',
            command=self.select_all_bookmarks,
        ).grid(row=0, column=0, sticky='w')

        # Create a button to download all selected bookmarks as mp3s
        ttk.Button(
            button_frame,
            text='Download MP3s',
            command=lambda: self.download_mp3s(textbox)
        ).grid(row=0, column=1, sticky='e')

        # Create a button to download all selected bookmarks as videos
        ttk.Button(
            button_frame,
            text='Download videos',
            command=lambda: self.download_videos(textbox)
        ).grid(row=0, column=2)

    @staticmethod
    def select_bookmark(bookmark: Bookmark, is_selected):
        """
        :param bookmark: 'Bookmark'. An element of the bookmarks instance list
        :param is_selected: The state of the rendered bookmark's ttk.Checkbutton variable
        :return: None
        """
        bookmark.is_selected = is_selected

    def select_all_bookmarks(self):
        # Set all loaded bookmarks' is_selected to True
        for b in self.bookmarks:
            b.is_selected = True

        # Set all rendered bookmarks' ttk.Checkbutton variables to True, and check the buttons
        for bs in self.bookmarks_state:
            bs.set(True)

    @staticmethod
    def output_message(textbox: tk.Text, message: str):
        textbox.insert(tk.END, message + '\n')

    def clear_frame(self, frame: tk.Frame):
        # Clear the ttk.Checkbutton variables, representing the is_selected state of the *rendered* bookmarks
        # The loaded bookmarks are rewritten at the press of the 'Load bookmarks' button
        self.bookmarks_state = []

        # Clear the rendered elements in the parent frame
        for element in frame.grid_slaves():
            element.destroy()

    def download_videos(self, textbox: tk.Text):
        # All bookmarks where is_selected is True
        bookmarks_to_download = [b for b in self.bookmarks if b.is_selected]

        for b in bookmarks_to_download:
            self.output_message(textbox, message=f'Downloading "{b.title}"')
            try:
                self.download_video(b.url, textbox)
            except Exception as e:
                self.output_message(textbox, message=str(e))

    def download_video(self, url, textbox: tk.Text, output_path='Downloads'):
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # Download the best video and audio separately
            'outtmpl': output_path + '/%(title)s.%(ext)s',  # Template for output filename
            'merge_output_format': 'mkv',  # Merge into mp4 format
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',  # Ensures conversion if needed
                'preferedformat': 'mkv',  # Preferred format for the output file
            }],
            'noplaylist': True,  # Do not download the entire playlist, only the video
            'playlist_items': '1',  # Only download the first video if it's a playlist
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', None)

            self.output_message(textbox, message=f'"{title}" was downloaded successfully')

    def download_mp3s(self, textbox: tk.Text):
        # All bookmarks where is_selected is True
        bookmarks_to_download = [b for b in self.bookmarks if b.is_selected]

        for b in bookmarks_to_download:
            self.output_message(textbox, message=f'Downloading "{b.title}"')
            try:
                self.download_mp3(b.url, textbox)
            except Exception as e:
                self.output_message(textbox, message=str(e))

    def download_mp3(self, url, textbox: tk.Text, output_path='Downloads'):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path + '/%(title)s.%(ext)s',  # Save as original format first
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',  # '0' ensures the best possible quality
            }],
            'noplaylist': True,  # Do not download the entire playlist, only the video
            'playlist_items': '1',  # Only download the first video if it's a playlist
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract and download the first video only
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', None)

            self.output_message(textbox, message=f'"{title}" was downloaded successfully')

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    youtube_downloader = YoutubeDownloader()
    youtube_downloader.run()
