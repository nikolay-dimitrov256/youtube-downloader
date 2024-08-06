import tkinter as tk
from tkinter import ttk
from typing import Optional

from loaders import BookmarkLoader


class YoutubeDownloader:
    def __init__(self):
        self.loader: Optional[BookmarkLoader] = None
        self.root = tk.Tk()
        self.root.title('Youtube Downloader')

        self.render_widgets()

    def render_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack()

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

    def download_video(self, url):
        print(url)

    def download_mp3(self, url):
        print(url)

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    youtube_downloader = YoutubeDownloader()
    youtube_downloader.run()