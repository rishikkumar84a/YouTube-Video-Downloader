# YouTube Video Downloader

A modern, user-friendly application for downloading YouTube videos with a clean UI.

## Features

- Download YouTube videos in various resolutions
- Select your preferred download location
- View video thumbnails and titles before downloading
- Real-time download progress tracking
- Responsive and modern user interface
- Fallback option using yt-dlp if pytube encounters issues

## Requirements

- Python 3.7+
- Required Python packages (install using `pip install -r requirements.txt`):
  - pytube
  - customtkinter
  - pillow
  - Optional: yt-dlp (for fallback downloader)

## Installation

1. Clone or download this repository
2. Install the required packages:

```
pip install -r requirements.txt
```

3. Optional: Install yt-dlp for the fallback downloader (recommended):

```
pip install yt-dlp
```

## Usage

### Main Application

1. Run the application:

```
python youtube_downloader.py
```

2. Enter a YouTube URL in the input field
3. Click "Fetch Video Info" to load the video details
4. Select your preferred resolution from the dropdown menu
5. Choose a download location (defaults to your system's Downloads folder)
6. Click "Download Video" to start the download
7. Monitor the download progress in real-time

### Fallback Downloader (if the main app has issues)

If the main application encounters issues with YouTube API changes, you can use the fallback downloader:

```
python fallback_downloader.py
```

The fallback downloader uses yt-dlp, which is more resistant to YouTube API changes. It has options to:
- Download best video quality
- Download audio only (MP3)

## Error Handling

The application handles various error scenarios:
- Invalid YouTube URLs
- Network connection issues
- Unavailable video resolutions
- Invalid download paths

## Troubleshooting

### "Bad Request" or Fetching Errors
If you encounter errors when fetching video information:
- Make sure you're using a valid YouTube URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID)
- Check your internet connection
- The application includes patches for common pytube issues with YouTube's API
- Try copying the video URL directly from YouTube's share button
- If issues persist, use the fallback downloader (`fallback_downloader.py`)

### Other Issues
- Ensure you have the latest version of the required packages
- Some videos might be restricted and cannot be downloaded
- YouTube occasionally changes their API which may affect functionality
- For persistent issues, try updating pytube: `pip install --upgrade pytube`

## Screenshots

(Add screenshots here when available)

## License

This project is available for personal use.

## Acknowledgements

- Built with [pytube](https://github.com/pytube/pytube)
- UI created with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Fallback functionality provided by [yt-dlp](https://github.com/yt-dlp/yt-dlp) 