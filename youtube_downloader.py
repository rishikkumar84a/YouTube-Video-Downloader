import os
import threading
import tkinter
import re
import json
from tkinter import filedialog
import customtkinter as ctk
from pytube import YouTube
from PIL import Image, ImageTk
import urllib.request
from io import BytesIO
import traceback

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Fix for pytube
def patch_pytube():
    """Apply compatible patches to pytube for current version"""
    # Update client versions for age-restricted videos
    from pytube import innertube
    if hasattr(innertube, "_default_clients"):
        # Default header to use for all clients
        default_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        # Default API key
        api_key = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
        
        # Update client configurations with headers and API key
        innertube._default_clients = {
            "ANDROID": {
                "context": {"client": {"clientName": "ANDROID", "clientVersion": "17.31.35"}},
                "header": default_header,
                "api_key": api_key
            },
            "WEB": {
                "context": {"client": {"clientName": "WEB", "clientVersion": "2.20220801.00.00"}},
                "header": default_header,
                "api_key": api_key
            },
            "ANDROID_MUSIC": {
                "context": {"client": {"clientName": "ANDROID_MUSIC", "clientVersion": "5.16.51"}},
                "header": default_header,
                "api_key": api_key
            },
            "WEB_MUSIC": {
                "context": {"client": {"clientName": "WEB_MUSIC", "clientVersion": "2.20220801.00.00"}},
                "header": default_header,
                "api_key": api_key
            },
            "WEB_CREATOR": {
                "context": {"client": {"clientName": "WEB_CREATOR", "clientVersion": "1.20220801.00.00"}},
                "header": default_header,
                "api_key": api_key
            },
            "ANDROID_CREATOR": {
                "context": {"client": {"clientName": "ANDROID_CREATOR", "clientVersion": "22.30.100"}},
                "header": default_header,
                "api_key": api_key
            },
            "TV_EMBEDDED": {
                "context": {"client": {"clientName": "TVHTML5_SIMPLY_EMBEDDED_PLAYER", "clientVersion": "2.0"}},
                "header": default_header,
                "api_key": api_key
            },
        }

    # Fix for cipher issues
    from pytube import cipher
    if hasattr(cipher, "get_initial_function_name"):
        old_get_initial_function_name = cipher.get_initial_function_name
        def new_get_initial_function_name(js):
            try:
                return old_get_initial_function_name(js)
            except Exception as ex:
                print(f"Cipher function name extraction failed: {ex}")
                # Try common function names used by YouTube
                return "Lpb"
        cipher.get_initial_function_name = new_get_initial_function_name

    # Fix for throttling function name
    if hasattr(cipher, "get_throttling_function_name"):
        old_get_throttling_function_name = cipher.get_throttling_function_name
        def new_get_throttling_function_name(js):
            try:
                return old_get_throttling_function_name(js)
            except Exception as ex:
                print(f"Throttling function name extraction failed: {ex}")
                # Try common function names used by YouTube
                return "js"
        cipher.get_throttling_function_name = new_get_throttling_function_name

    # Fix for js_url extraction only if needed
    from pytube import extract
    if hasattr(extract, "js_url"):
        old_js_url = extract.js_url
        def new_js_url(html, age_restricted=False):
            try:
                return old_js_url(html, age_restricted)
            except Exception as ex:
                print(f"JS URL extraction failed: {ex}")
                # Try a common pattern in the HTML
                pattern = r'["\'](/s/player/[a-zA-Z0-9_-]+/player_ias.vflset/[a-zA-Z0-9_-]+/base.js)["\']'
                match = re.search(pattern, html)
                if match:
                    return f"https://www.youtube.com{match.group(1)}"
                # If all else fails, use a recent known base.js URL
                return "https://www.youtube.com/s/player/f8c67d75/player_ias.vflset/en_US/base.js"
        extract.js_url = new_js_url

# Apply patches
patch_pytube()

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("YouTube Video Downloader")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # Variables
        self.url_var = tkinter.StringVar()
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.thumbnail_image = None
        self.download_thread = None
        
        # Create UI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Create main frame
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=0)  # Header
        main_frame.grid_rowconfigure(1, weight=1)  # Content
        main_frame.grid_rowconfigure(2, weight=0)  # Footer
        
        # Header
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="YouTube Video Downloader", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Content
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Left panel - Input section
        input_frame = ctk.CTkFrame(content_frame)
        input_frame.grid(row=0, column=0, padx=(0, 5), pady=0, sticky="nsew")
        
        input_frame.grid_columnconfigure(0, weight=1)
        
        # URL input
        url_label = ctk.CTkLabel(
            input_frame, 
            text="Enter YouTube URL:", 
            font=ctk.CTkFont(size=16)
        )
        url_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        url_entry = ctk.CTkEntry(
            input_frame, 
            textvariable=self.url_var, 
            height=40, 
            font=ctk.CTkFont(size=14)
        )
        url_entry.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Fetch button
        fetch_button = ctk.CTkButton(
            input_frame, 
            text="Fetch Video Info", 
            height=40, 
            font=ctk.CTkFont(size=14), 
            command=self.fetch_video
        )
        fetch_button.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Resolution selector
        resolution_label = ctk.CTkLabel(
            input_frame, 
            text="Select Resolution:", 
            font=ctk.CTkFont(size=16)
        )
        resolution_label.grid(row=3, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.resolution_combobox = ctk.CTkComboBox(
            input_frame, 
            values=["Select a video first"], 
            state="disabled", 
            height=40, 
            font=ctk.CTkFont(size=14)
        )
        self.resolution_combobox.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Download location
        location_label = ctk.CTkLabel(
            input_frame, 
            text="Download Location:", 
            font=ctk.CTkFont(size=16)
        )
        location_label.grid(row=5, column=0, padx=20, pady=(10, 5), sticky="w")
        
        location_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        location_frame.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        location_frame.grid_columnconfigure(0, weight=1)
        location_frame.grid_columnconfigure(1, weight=0)
        
        self.location_entry = ctk.CTkEntry(
            location_frame, 
            height=40, 
            font=ctk.CTkFont(size=14)
        )
        self.location_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.location_entry.insert(0, self.download_path)
        
        browse_button = ctk.CTkButton(
            location_frame, 
            text="Browse", 
            width=100, 
            height=40, 
            font=ctk.CTkFont(size=14), 
            command=self.browse_location
        )
        browse_button.grid(row=0, column=1)
        
        # Download button
        self.download_button = ctk.CTkButton(
            input_frame, 
            text="Download Video", 
            height=50, 
            font=ctk.CTkFont(size=16, weight="bold"), 
            command=self.download_video,
            state="disabled"
        )
        self.download_button.grid(row=7, column=0, padx=20, pady=(20, 20), sticky="ew")
        
        # Right panel - Video info
        info_frame = ctk.CTkFrame(content_frame)
        info_frame.grid(row=0, column=1, padx=(5, 0), pady=0, sticky="nsew")
        
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_rowconfigure(3, weight=1)
        
        # Thumbnail
        thumbnail_label = ctk.CTkLabel(
            info_frame, 
            text="Video Thumbnail", 
            font=ctk.CTkFont(size=16)
        )
        thumbnail_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.thumbnail_frame = ctk.CTkFrame(info_frame, fg_color="#1a1a1a", corner_radius=10)
        self.thumbnail_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.thumbnail_label = ctk.CTkLabel(self.thumbnail_frame, text="No video selected", image=None)
        self.thumbnail_label.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Video title
        title_info_label = ctk.CTkLabel(
            info_frame, 
            text="Video Title:", 
            font=ctk.CTkFont(size=16)
        )
        title_info_label.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.video_title_label = ctk.CTkLabel(
            info_frame, 
            text="No video selected", 
            font=ctk.CTkFont(size=14), 
            wraplength=350
        )
        self.video_title_label.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nw")
        
        # Progress Frame
        self.progress_frame = ctk.CTkFrame(info_frame)
        self.progress_frame.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame, 
            text="Download Progress:", 
            font=ctk.CTkFont(size=14)
        )
        self.progress_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 10))
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            self.progress_frame, 
            text="", 
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Footer
        footer_frame = ctk.CTkFrame(main_frame)
        footer_frame.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")
        
        footer_label = ctk.CTkLabel(
            footer_frame, 
            text="Created with pytube and CustomTkinter", 
            font=ctk.CTkFont(size=12)
        )
        footer_label.pack(pady=10)
        
        # Add fallback information
        fallback_label = ctk.CTkLabel(
            footer_frame, 
            text="If you have issues, try the fallback downloader: python fallback_downloader.py", 
            font=ctk.CTkFont(size=11)
        )
        fallback_label.pack(pady=(0, 5))
    
    def browse_location(self):
        """Open file dialog to select download location"""
        directory = filedialog.askdirectory(initialdir=self.download_path)
        if directory:
            self.download_path = directory
            self.location_entry.delete(0, tkinter.END)
            self.location_entry.insert(0, self.download_path)
    
    def fetch_video(self):
        """Fetch video information from YouTube"""
        url = self.url_var.get().strip()
        if not url:
            self.show_error("Please enter a YouTube URL")
            return
        
        # Validate and clean the URL
        url = self.clean_url(url)
        if not url:
            self.show_error("Invalid YouTube URL format")
            return
        
        self.status_label.configure(text="Fetching video info...")
        
        # Start a new thread for fetching video info
        threading.Thread(target=self._fetch_video_thread, args=(url,), daemon=True).start()
    
    def clean_url(self, url):
        """Clean and validate YouTube URL"""
        # Check if it's a valid YouTube URL
        youtube_regex = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
        match = re.match(youtube_regex, url)
        
        if not match:
            return None
        
        # Extract video ID and create a clean URL
        video_id = match.group(4)
        return f'https://www.youtube.com/watch?v={video_id}'
    
    def _fetch_video_thread(self, url):
        """Background thread for fetching video info"""
        try:
            # Create YouTube object with additional parameters
            yt = YouTube(
                url,
                use_oauth=False,
                allow_oauth_cache=False,
                on_progress_callback=self.on_progress
            )
            
            # Get video title
            title = yt.title
            
            # Get available resolutions
            streams = yt.streams.filter(progressive=True).order_by('resolution').desc()
            resolutions = [stream.resolution for stream in streams]
            
            # Get thumbnail
            thumbnail_url = yt.thumbnail_url
            
            # Update UI on the main thread
            self.after(0, lambda: self._update_ui_after_fetch(title, resolutions, thumbnail_url, yt))
            
        except Exception as error:
            error_details = traceback.format_exc()
            print(f"Error fetching video: {error}")
            print(f"Traceback: {error_details}")
            self.after(0, lambda: self.show_error(f"Error fetching video: {str(error)}"))
    
    def _update_ui_after_fetch(self, title, resolutions, thumbnail_url, yt):
        """Update UI with fetched video information"""
        # Update video title
        self.video_title_label.configure(text=title)
        
        # Update resolutions dropdown
        if not resolutions:
            self.show_error("No downloadable streams found for this video")
            return
            
        self.resolution_combobox.configure(values=resolutions, state="normal")
        self.resolution_combobox.set(resolutions[0])
        
        # Store YouTube object for later use
        self.yt = yt
        
        # Load and display thumbnail
        self.load_thumbnail(thumbnail_url)
        
        # Enable download button
        self.download_button.configure(state="normal")
        
        # Update status
        self.status_label.configure(text="Video info fetched successfully!")
    
    def load_thumbnail(self, url):
        """Load and display thumbnail image"""
        try:
            # Fetch the image
            response = urllib.request.urlopen(url)
            image_data = response.read()
            
            # Create PIL Image
            pil_image = Image.open(BytesIO(image_data))
            
            # Resize the image to fit in our UI (maintain aspect ratio)
            target_width = 350
            width_percent = target_width / float(pil_image.size[0])
            target_height = int(float(pil_image.size[1]) * float(width_percent))
            pil_image = pil_image.resize((target_width, target_height), Image.LANCZOS)
            
            # Convert to CTkImage
            self.thumbnail_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, 
                                               size=(target_width, target_height))
            
            # Update label
            self.thumbnail_label.configure(image=self.thumbnail_image, text="")
            
        except Exception as error:
            print(f"Thumbnail error: {error}")
            self.thumbnail_label.configure(text=f"Could not load thumbnail: {str(error)}")
    
    def download_video(self):
        """Start video download process"""
        if not hasattr(self, 'yt'):
            self.show_error("Please fetch a video first")
            return
        
        # Get selected resolution
        resolution = self.resolution_combobox.get()
        if not resolution or resolution == "Select a video first":
            self.show_error("Please select a resolution")
            return
        
        # Get download path
        download_path = self.location_entry.get()
        if not download_path:
            self.show_error("Please specify a download location")
            return
        
        # Create directory if it doesn't exist
        os.makedirs(download_path, exist_ok=True)
        
        # Disable UI elements during download
        self.download_button.configure(state="disabled")
        self.resolution_combobox.configure(state="disabled")
        
        # Reset progress
        self.progress_bar.set(0)
        self.status_label.configure(text="Starting download...")
        
        # Start download in a new thread
        self.download_thread = threading.Thread(
            target=self._download_video_thread, 
            args=(resolution, download_path),
            daemon=True
        )
        self.download_thread.start()
    
    def _download_video_thread(self, resolution, download_path):
        """Background thread for downloading video"""
        try:
            # Register progress callback
            self.yt.register_on_progress_callback(self.on_progress)
            
            # Get the stream with selected resolution
            stream = self.yt.streams.filter(progressive=True, resolution=resolution).first()
            
            if not stream:
                # Try to find the closest available resolution
                all_streams = self.yt.streams.filter(progressive=True).order_by('resolution')
                if all_streams:
                    stream = all_streams.last()  # Get highest available resolution
                    resolution_message = f"Using closest available resolution: {stream.resolution}"
                    self.after(0, lambda: self.status_label.configure(text=resolution_message))
                else:
                    self.after(0, lambda: self.show_error(f"No stream available for resolution {resolution}"))
                    self.after(0, lambda: self._reset_ui_after_download())
                    return
            
            # Download the video
            video_path = stream.download(output_path=download_path)
            
            # Update UI on the main thread
            self.after(0, lambda: self._download_complete(video_path))
            
        except Exception as error:
            error_details = traceback.format_exc()
            print(f"Error during download: {error}")
            print(f"Traceback: {error_details}")
            self.after(0, lambda: self.show_error(f"Error during download: {str(error)}"))
            self.after(0, lambda: self._reset_ui_after_download())
    
    def on_progress(self, stream, chunk, bytes_remaining):
        """Progress callback for download"""
        if not stream or not hasattr(stream, 'filesize') or stream.filesize is None:
            return
            
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = bytes_downloaded / total_size
        
        # Update progress bar
        self.after(0, lambda: self.progress_bar.set(percentage))
        
        # Update status text
        status_text = f"Downloaded: {self._format_size(bytes_downloaded)} of {self._format_size(total_size)} ({int(percentage*100)}%)"
        self.after(0, lambda: self.status_label.configure(text=status_text))
    
    def _format_size(self, bytes):
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} TB"
    
    def _download_complete(self, video_path):
        """Handle download completion"""
        self.status_label.configure(text=f"Download complete! Saved to: {os.path.basename(video_path)}")
        self.progress_bar.set(1.0)
        self._reset_ui_after_download()
    
    def _reset_ui_after_download(self):
        """Reset UI elements after download"""
        self.download_button.configure(state="normal")
        self.resolution_combobox.configure(state="normal")
    
    def show_error(self, message):
        """Display error message"""
        self.status_label.configure(text=f"Error: {message}")

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop() 