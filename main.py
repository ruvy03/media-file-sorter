import tkinter as tk
from gui import FileOrganizerGUI
import sys
import os

def setup_environment():
    import mimetypes
    mimetypes.init()
    mimetypes.add_type('image/webp', '.webp')
    mimetypes.add_type('image/heic', '.heic')
    mimetypes.add_type('video/mp4', '.mp4')
    mimetypes.add_type('audio/mp3', '.mp3')

def main():
    try:
        setup_environment()
        root = tk.Tk()
        try:
            if getattr(sys, 'frozen', False):
                application_path = sys._MEIPASS
            else:
                application_path = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(application_path, 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not load application icon: {e}")
        app = FileOrganizerGUI(root)
        root.mainloop()
    except Exception as e:
        tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()