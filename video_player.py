import tkinter as tk
from tkinter import ttk
import vlc
import os

class VideoPlayer:
    def __init__(self, parent, width=400, height=300):
        """Initialize the video player with VLC backend."""
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        
        # Create a frame to hold the video
        self.frame = ttk.Frame(parent)
        
        if os.name == "nt":  # Windows
            self.player.set_hwnd(self.frame.winfo_id())
        else:  # Linux/Mac
            self.player.set_xwindow(self.frame.winfo_id())
            
        self.frame.configure(width=width, height=height)
        
        # Create control buttons frame
        self.controls = ttk.Frame(parent)
        
        # Play/Pause button
        self.play_button = ttk.Button(self.controls, text="Play", command=self.toggle_play)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        # Volume control slider
        self.volume_scale = ttk.Scale(
            self.controls,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.set_volume
        )
        self.volume_scale.set(100)
        self.volume_scale.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_scale = ttk.Scale(
            self.controls,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.seek
        )
        self.progress_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Update progress bar periodically
        self._update_progress()
        
    def load_video(self, path: str):
        """Load a video file into the player."""
        media = self.instance.media_new(path)
        self.player.set_media(media)
        
    def toggle_play(self):
        """Toggle between play and pause states."""
        if self.player.is_playing():
            self.player.pause()
            self.play_button.configure(text="Play")
        else:
            self.player.play()
            self.play_button.configure(text="Pause")
            
    def set_volume(self, value):
        """Set the player volume."""
        self.player.audio_set_volume(int(float(value)))
        
    def seek(self, value):
        """Seek to a specific position in the video."""
        self.player.set_position(float(value) / 100.0)
        
    def _update_progress(self):
        """Update the progress bar to match video position."""
        if self.player.is_playing():
            position = self.player.get_position() * 100
            self.progress_scale.set(position)
        self.frame.after(1000, self._update_progress)  # Update every second
        
    def stop(self):
        """Stop video playback."""
        self.player.stop()
        self.play_button.configure(text="Play")
        
    def cleanup(self):
        """Release all resources."""
        self.stop()
        self.player.release()
        self.instance.release()