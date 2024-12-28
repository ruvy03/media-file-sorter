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
        self.play_button = ttk.Button(self.controls, text="Pause", command=self.toggle_play)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        # Volume control
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
        self.progress_var = tk.DoubleVar()
        self.progress_scale = ttk.Scale(
            self.controls,
            from_=0,
            to=1000,
            orient=tk.HORIZONTAL,
            variable=self.progress_var
        )
        self.progress_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Bind events for seeking
        self.progress_scale.bind("<Button-1>", self.start_seek)
        self.progress_scale.bind("<ButtonRelease-1>", self.end_seek)
        
        self.is_seeking = False
        self.update_id = None
        
    def start_seek(self, event):
        """Called when user starts dragging the seek bar"""
        self.is_seeking = True
        
    def end_seek(self, event):
        """Called when user releases the seek bar"""
        if self.is_seeking:
            # Get the final position and seek there
            pos = self.progress_var.get() / 1000.0
            self.player.set_position(pos)
            self.is_seeking = False
        
    def load_video(self, path: str):
        """Load a video file into the player."""
        self.stop()  # Stop any existing playback
        
        media = self.instance.media_new(str(path))
        self.player.set_media(media)
        
        # Wait for media to be parsed
        media.parse()
        
        self.player.play()
        self.play_button.configure(text="Pause")
        self._start_progress_update()
            
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
            
    def _start_progress_update(self):
        """Start the progress update timer."""
        if self.update_id:
            self.frame.after_cancel(self.update_id)
        self._update_progress()
        
    def _update_progress(self):
        """Update the progress bar to match video position."""
        if self.player.is_playing() and not self.is_seeking:
            try:
                position = self.player.get_position() * 1000
                self.progress_var.set(position)
            except:
                pass
        self.update_id = self.frame.after(100, self._update_progress)
        
    def stop(self):
        """Stop video playback."""
        if self.update_id:
            self.frame.after_cancel(self.update_id)
            self.update_id = None
        self.player.stop()
        self.progress_var.set(0)
        self.play_button.configure(text="Play")
        
    def cleanup(self):
        """Release all resources."""
        self.stop()
        self.player.release()
        self.instance.release()