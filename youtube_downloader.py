import json
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
                settings = json.loads(file.read())

                return settings
        except FileNotFoundError:
            return {}

    def save_settings(self):
        with open('settings.txt', 'w') as file:
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

        message_entry = ttk.Entry(download_frame, state='disabled', width=70)
        message_entry.grid(row=0, columnspan=2)

        url_frame = ttk.LabelFrame(download_frame, text='Enter URL:')
        url_frame.grid(row=2, columnspan=2, pady=(0, 10))

        url_entry = ttk.Entry(url_frame, width=70)
        url_entry.pack()

        ttk.Button(
            download_frame, text='Download mp3', command=lambda: self.download_mp3(url_entry.get())
        ).grid(row=4, column=0)
        ttk.Button(
            download_frame, text='Download video', command=lambda: self.download_video(url_entry.get())
        ).grid(row=4, column=1)

        ttk.Separator(download_frame).grid(row=6, columnspan=2, pady=10, sticky='we')

        message_frame = ttk.Frame(download_frame)
        message_frame.grid(row=7, columnspan=2)
        message_scroll = ttk.Scrollbar(message_frame)
        message_scroll.pack(side='right', fill='y')

        message_field = tk.Text(message_frame, width=50, height=20, yscrollcommand=message_scroll.set)
        message_field.pack()
        message_scroll.config(command=message_field.yview)

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
        if browser not in self.supported_browsers:
            return

        path = filedialog.askdirectory()
        self.settings[browser] = path

    def load_bookmarks(self, textbox: tk.Text, selected_browser, search, ascending, limit, parent_frame: ScrollableFrame, grandparent_frame: ttk.LabelFrame):
        loader = self.supported_browsers.get(selected_browser)
        if not loader:
            self.output_message(textbox, 'Please select a supported browser')
            return
        self.loader = loader()

        try:
            limit = int(limit)
        except ValueError:
            limit = None

        self.bookmarks = self.loader.load_bookmarks(search, ascending, limit)

        self.render_bookmarks(parent_frame, grandparent_frame)

    def render_bookmarks(self, parent_frame: ScrollableFrame, grand_parent_frame: ttk.LabelFrame):
        self.clear_frame(parent_frame.scrollable_frame)

        for index, bookmark in enumerate(self.bookmarks):
            self.render_single_bookmark(parent_frame.scrollable_frame, index, bookmark)

        self.render_footer_buttons(grand_parent_frame)

    def render_single_bookmark(self, parent: tk.Frame, row, bookmark: Bookmark) -> None:
        bookmark_frame = tk.Frame(parent)
        bookmark_frame.grid(row=row, column=0, sticky='we')

        is_selected = tk.BooleanVar()
        self.bookmarks_state.append(is_selected)

        selected_checkbutton = ttk.Checkbutton(
            bookmark_frame,
            variable=is_selected,
            command=lambda: self.select_bookmark(bookmark, is_selected.get()),
        )
        selected_checkbutton.grid(row=0, column=0, sticky='w')

        ttk.Label(bookmark_frame, text=bookmark.title).grid(row=0, column=1, sticky='we')

    def render_footer_buttons(self, grand_parent_frame: ttk.LabelFrame):
        button_frame = tk.Frame(grand_parent_frame)
        button_frame.grid(row=11, columnspan=2)
        ttk.Button(
            button_frame,
            text='Select all',
            command=self.select_all_bookmarks,
        ).grid(row=0, column=0)

    @staticmethod
    def select_bookmark(bookmark: Bookmark, is_selected):
        bookmark.is_selected = is_selected

    def select_all_bookmarks(self):
        for b in self.bookmarks:
            b.is_selected = True

        for bs in self.bookmarks_state:
            bs.set(True)

    @staticmethod
    def output_message(textbox: tk.Text, message: str):
        textbox.insert(tk.END, message + '\n')

    def clear_frame(self, frame: tk.Frame):
        self.bookmarks_state = []

        for element in frame.grid_slaves():
            element.destroy()

    def download_video(self, url):
        print(url)

    def download_mp3(self, url):
        print(url)

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    youtube_downloader = YoutubeDownloader()
    youtube_downloader.run()
