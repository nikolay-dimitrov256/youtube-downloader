import json
import tkinter as tk
from tkinter import ttk, filedialog
from typing import Optional

from loaders import BookmarkLoader, FirefoxLoader, ChromeLoader


class YoutubeDownloader:
    supported_browsers = {
        'Mozilla Firefox': FirefoxLoader,
        'Google Chrome': ChromeLoader,
    }

    def __init__(self):
        self.settings = self.load_settings()
        self.loader: Optional[BookmarkLoader] = None
        self.root = tk.Tk()
        self.root.title('Youtube Downloader')

        self.render_widgets()

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

    def output_entry_message(self, entry: ttk.Entry, message: str, color: str = 'black'):
        entry['state'] = tk.NORMAL
        entry.delete(0, tk.END)
        entry.insert(0, message)
        entry['foreground'] = color
        entry['state'] = tk.DISABLED

    def download_video(self, url):
        print(url)

    def download_mp3(self, url):
        print(url)

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    youtube_downloader = YoutubeDownloader()
    youtube_downloader.run()
