"""
Fallback YouTube Downloader using yt-dlp
-----------------------------------------
This is an alternative downloader that can be used if the main application 
has issues with the YouTube API changes.

Requirements:
- Install yt-dlp: pip install yt-dlp
"""

import os
import sys
import tkinter
from tkinter import filedialog
import customtkinter as ctk
import threading
import subprocess
import re
import json

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class FallbackDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Fallback YouTube Downloader (yt-dlp)")
        self.geometry("800x500")
        self.minsize(700, 400)
        
        # Variables
        self.url_var = tkinter.StringVar()
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        
        # Create UI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(2, weight=0)  # Footer
        
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Fallback YouTube Downloader (yt-dlp)", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Content
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(4, weight=1)
        
        # URL input
        url_label = ctk.CTkLabel(
            content_frame, 
            text="Enter YouTube URL:", 
            font=ctk.CTkFont(size=16)
        )
        url_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        url_entry = ctk.CTkEntry(
            content_frame, 
            textvariable=self.url_var, 
            height=40, 
            font=ctk.CTkFont(size=14)
        )
        url_entry.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Download location
        location_label = ctk.CTkLabel(
            content_frame, 
            text="Download Location:", 
            font=ctk.CTkFont(size=16)
        )
        location_label.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        
        location_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        location_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        
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
        
        # Download options
        options_frame = ctk.CTkFrame(content_frame)
        options_frame.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        options_frame.grid_columnconfigure(0, weight=1)
        options_frame.grid_columnconfigure(1, weight=1)
        
        audio_button = ctk.CTkButton(
            options_frame, 
            text="Download Audio Only (MP3)", 
            height=50, 
            font=ctk.CTkFont(size=14), 
            command=lambda: self.download_video(audio_only=True)
        )
        audio_button.grid(row=0, column=0, padx=(0, 10), pady=20, sticky="ew")
        
        video_button = ctk.CTkButton(
            options_frame, 
            text="Download Best Video", 
            height=50, 
            font=ctk.CTkFont(size=14), 
            command=lambda: self.download_video(audio_only=False)
        )
        video_button.grid(row=0, column=1, padx=(10, 0), pady=20, sticky="ew")
        
        # Log output
        log_label = ctk.CTkLabel(
            content_frame, 
            text="Output Log:", 
            font=ctk.CTkFont(size=14)
        )
        log_label.grid(row=5, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.log_textbox = ctk.CTkTextbox(content_frame, height=150)
        self.log_textbox.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.log_textbox.configure(state="disabled")
        
        # Footer
        footer_frame = ctk.CTkFrame(self)
        footer_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        footer_label = ctk.CTkLabel(
            footer_frame, 
            text="Using yt-dlp for downloading. If this tool doesn't work, make sure yt-dlp is installed.", 
            font=ctk.CTkFont(size=12)
        )
        footer_label.pack(pady=10)
        
        # Add ffmpeg message
        ffmpeg_label = ctk.CTkLabel(
            footer_frame, 
            text="Note: ffmpeg is required for merging video and audio. Install it if videos have no sound.", 
            font=ctk.CTkFont(size=11, slant="italic")
        )
        ffmpeg_label.pack(pady=(0, 5))
    
    def browse_location(self):
        """Open file dialog to select download location"""
        directory = filedialog.askdirectory(initialdir=self.download_path)
        if directory:
            self.download_path = directory
            self.location_entry.delete(0, tkinter.END)
            self.location_entry.insert(0, self.download_path)
    
    def download_video(self, audio_only=False):
        """Start video download process"""
        url = self.url_var.get().strip()
        if not url:
            self.log_message("Error: Please enter a YouTube URL")
            return
        
        download_path = self.location_entry.get()
        if not download_path:
            self.log_message("Error: Please specify a download location")
            return
        
        # Create directory if it doesn't exist
        os.makedirs(download_path, exist_ok=True)
        
        # Clear log
        self.clear_log()
        
        # Start download in a new thread
        threading.Thread(
            target=self._download_thread, 
            args=(url, download_path, audio_only),
            daemon=True
        ).start()
    
    def _download_thread(self, url, download_path, audio_only):
        """Background thread for downloading with yt-dlp"""
        try:
            self.log_message(f"Starting download for: {url}")
            self.log_message(f"Output directory: {download_path}")
            
            # Prepare command
            command = ["yt-dlp"]
            
            if audio_only:
                self.log_message("Mode: Audio only (MP3)")
                command.extend([
                    "-x", "--audio-format", "mp3",
                    "--audio-quality", "0",
                    "-o", os.path.join(download_path, "%(title)s.%(ext)s")
                ])
            else:
                self.log_message("Mode: Best video quality")
                command.extend([
                    "-f", "bestvideo+bestaudio/best",
                    "--merge-output-format", "mp4",
                    "-o", os.path.join(download_path, "%(title)s.%(ext)s")
                ])
            
            # Add URL
            command.append(url)
            
            # Run command and capture output
            self.log_message("Running yt-dlp command...")
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read and display output
            for line in process.stdout:
                self.log_message(line.strip())
            
            # Wait for process to complete
            process.wait()
            
            if process.returncode == 0:
                self.log_message("Download completed successfully!")
            else:
                self.log_message(f"Download failed with exit code {process.returncode}")
                
        except FileNotFoundError:
            self.log_message("Error: yt-dlp not found. Please install it using 'pip install yt-dlp'")
        except Exception as e:
            self.log_message(f"Error during download: {str(e)}")
    
    def log_message(self, message):
        """Add message to log textbox"""
        def _update_log():
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", message + "\n")
            self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")
        
        self.after(0, _update_log)
    
    def clear_log(self):
        """Clear log textbox"""
        def _clear_log():
            self.log_textbox.configure(state="normal")
            self.log_textbox.delete("1.0", "end")
            self.log_textbox.configure(state="disabled")
        
        self.after(0, _clear_log)

if __name__ == "__main__":
    app = FallbackDownloaderApp()
    app.mainloop() 