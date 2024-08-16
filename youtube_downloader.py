import json
import tkinter as tk
from tkinter import ttk, filedialog
from typing import Optional, List

from bookmark import Bookmark
from loaders import BookmarkLoader, FirefoxLoader, ChromeLoader


class YoutubeDownloader:
    supported_browsers = {
        'Mozilla Firefox': FirefoxLoader,
        'Google Chrome': ChromeLoader,
    }

    def __init__(self):
        self.settings = self.load_settings()
        self.loader: Optional[BookmarkLoader] = None
        self.bookmarks: List[Bookmark] = []
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

        loaded_bookmarks_frame = ttk.Frame(bookmarks_frame, width=500, height=350)
        loaded_bookmarks_frame.grid(row=9, columnspan=2, sticky='we')
        loaded_bookmarks_frame.grid_propagate(False)

        loaded_bookmarks_canvas = tk.Canvas(
            loaded_bookmarks_frame,
            scrollregion=(0, 0, 1000, 1000),
        )
        loaded_bookmarks_canvas.pack(expand=True, fill='both')
        loaded_bookmarks_canvas.grid_propagate(False)

        # mousewheel scrolling
        loaded_bookmarks_canvas.bind(
            '<MouseWheel>',
            lambda event: loaded_bookmarks_canvas.yview_scroll(int(event.delta // 60), 'units'),
        )

        bookmarks_y_scroll = ttk.Scrollbar(
            loaded_bookmarks_frame,
            orient='vertical',
            command=loaded_bookmarks_canvas.yview,
        )
        loaded_bookmarks_canvas.configure(yscrollcommand=bookmarks_y_scroll.set)
        bookmarks_y_scroll.place(relx=1, rely=0, relheight=1, anchor='ne')

        bookmarks_x_scroll = ttk.Scrollbar(
            loaded_bookmarks_frame,
            orient='horizontal',
            command=loaded_bookmarks_canvas.xview,
        )
        loaded_bookmarks_canvas.configure(xscrollcommand=bookmarks_x_scroll.set)
        bookmarks_x_scroll.place(relx=0, rely=1, relwidth=1, anchor='sw')

        # bookmarks_y_scroll = ttk.Scrollbar(loaded_bookmarks_frame, orient=tk.VERTICAL)
        # bookmarks_y_scroll.grid(row=0, column=1, sticky='ns')
        # # bookmarks_y_scroll.pack(side='right', fill='y')
        # bookmarks_x_scroll = ttk.Scrollbar(loaded_bookmarks_frame, orient=tk.HORIZONTAL)
        # bookmarks_x_scroll.grid(row=1, column=0, sticky='ew')
        # # bookmarks_x_scroll.pack(side='bottom', fill='x')
        #
        # loaded_bookmarks_canvas = tk.Canvas(
        #     loaded_bookmarks_frame,
        #     # yscrollcommand=bookmarks_y_scroll.set,
        #     # xscrollcommand=bookmarks_x_scroll.set,
        #     width=500,
        #     height=300,
        #     scrollregion=(0, 0, 1000, 1000)
        # )
        # loaded_bookmarks_canvas.grid(row=0, column=0, sticky='ew')
        # # loaded_bookmarks_canvas.pack(side='left', fill='both')
        # loaded_bookmarks_canvas.grid_propagate(False)
        # # loaded_bookmarks_canvas.pack_propagate(False)
        # bookmarks_y_scroll.config(command=loaded_bookmarks_canvas.yview)
        # bookmarks_x_scroll.config(command=loaded_bookmarks_canvas.xview)

        ttk.Button(
            bookmarks_frame,
            text='Load Bookmarks',
            command=lambda: self.load_bookmarks(
                message_field,
                current_browser.get(),
                search_field.get(),
                ascending.get(),
                number_entry.get(),
                loaded_bookmarks_canvas,
            ),
        ).grid(row=7, column=1, sticky='e', pady=5)

        ttk.Separator(bookmarks_frame).grid(row=8, columnspan=2, sticky='we', pady=5)

    def render_settings_tab(self, settings_frame: ttk.Frame):
        # message_entry = ttk.Entry(settings_frame, state=tk.DISABLED)
        # message_entry.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        # self.output_entry_message(message_entry, 'Chose a browser', 'green')

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

    def load_bookmarks(self, textbox: tk.Text, selected_browser, search, ascending, limit, bookmarks_canvas: tk.Canvas):
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

        self.render_bookmarks(bookmarks_canvas)

    def render_bookmarks(self, canvas: tk.Canvas):
        self.clear_canvas(canvas)

        for index, bookmark in enumerate(self.bookmarks):
            self.render_single_bookmark(canvas, index, bookmark)

    @staticmethod
    def render_single_bookmark(parent, row, bookmark: Bookmark) -> None:
        def select_bookmark(bookmark_: Bookmark, is_selected_):
            bookmark_.is_selected = is_selected_

        bookmark_frame = ttk.Frame(parent)
        bookmark_frame.grid(row=row, column=0, sticky='we')

        is_selected = tk.BooleanVar()
        selected_checkbutton = ttk.Checkbutton(
            bookmark_frame,
            variable=is_selected,
            command=lambda: select_bookmark(bookmark, is_selected.get()),
        )
        selected_checkbutton.grid(row=0, column=0, sticky='w')

        ttk.Label(bookmark_frame, text=bookmark.title).grid(row=0, column=1, sticky='we')

    @staticmethod
    def output_message(textbox: tk.Text, message: str):
        textbox.insert(tk.END, message + '\n')

    @staticmethod
    def clear_canvas(canvas: tk.Canvas):
        for element in canvas.grid_slaves():
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
