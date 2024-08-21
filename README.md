# YouTube Downloader

## Description

This program downloads YouTube videos as video files or mp3s.
The user can download by pasting a single url, or by loading multiple urls from the browser's bookmarks a batch download them with a single click. 
Currently Google Chrome and Mozilla Firefox are supported.

## Requirements

Before using the program, the user needs to have FFmpeg installed and added to the system PATH. Instructions are below.

In case of loading bookmarks from the browser, the user needs to specify, in the "Settings" tab, the path to the directory, where the respective browser bookmarks file is.
In Chrome the file is called Bookmarks, and for Firefox, places.sqlite. The path is usually as follows:

### On Windows:  

For **Google Chrome**:  
C:/Users/<username>/AppData/Local/Google/Chrome/User Data/Default

For **Mozilla Firefox**:  
C:/Users/<username>/AppData/Roaming/Mozilla/Firefox/Profiles/tarigwgs.default-release

## How to install ffmpeg:  
>### On Windows:
>
>1. Download FFmpeg
Go to the official FFmpeg website.
Under "Get packages & executable files," click on the "Windows" link.
You'll be directed to a page with different builds of FFmpeg. Click on the link to gyan.dev or BtbN (these are reliable sources for FFmpeg builds).
On the page, find the section for the latest stable release. Download the version labeled "Release" with the "full" build (it includes all libraries and codecs).
>2. Extract the Downloaded File
The downloaded file will be a ZIP archive. Right-click on it and select "Extract All..." to extract its contents.
Choose a location on your computer where you want to extract the files (e.g., C:\ffmpeg).
>3. Add FFmpeg to the System Path
To use FFmpeg from the command line, you need to add it to your system's PATH environment variable:
>
>Open System Properties:
>
>Right-click on "This PC" or "My Computer" on your desktop or in File Explorer.
Click on "Properties."
Click on "Advanced system settings" on the left side.
In the System Properties window, click on the "Environment Variables..." button.
Edit the Path Variable:
>
>In the Environment Variables window, under "System variables," scroll down and find the Path variable.
Select it and click "Edit..."
In the Edit Environment Variable window, click "New" and add the path to the bin folder within the FFmpeg directory. If you extracted FFmpeg to C:\ffmpeg, the path would be C:\ffmpeg\bin.
Click "OK" to close all windows.
>4. Verify the Installation
Open a new Command Prompt window.
Type ffmpeg and press Enter.
If FFmpeg is correctly installed, you'll see information about FFmpeg and its usage.

>### On macOS:
>```commandline
>brew install ffmpeg
>```

>### On Linux:
>```commandline
>sudo apt-get install ffmpeg
>```

