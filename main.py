import tkinter as tk  # Importing the tkinter library for GUI creation
from gui import FileOrganizerGUI  # Importing the FileOrganizerGUI class from the gui module
import sys  # Importing sys to access system-specific parameters and functions
import os  # Importing os for operating system dependent functionality

def setup_environment():
    """Set up any necessary environment variables or configurations."""
    # This function is responsible for initializing any necessary environment settings.
    
    # Importing mimetypes to handle file types and extensions
    import mimetypes
    mimetypes.init()  # Initialize the mimetypes database
    
    # Adding custom MIME types that may not be registered by default
    mimetypes.add_type('image/webp', '.webp')  # Register WebP image format
    mimetypes.add_type('image/heic', '.heic')  # Register HEIC image format
    mimetypes.add_type('video/mp4', '.mp4')  # Register MP4 video format
    mimetypes.add_type('audio/mp3', '.mp3')  # Register MP3 audio format

def main():
    """Main entry point of the application."""
    try:
        # Set up environment configurations before starting the application
        setup_environment()
        
        # Create the main window for the application using tkinter
        root = tk.Tk()
        
        # Attempt to set an application icon if available
        try:
            if getattr(sys, 'frozen', False):
                # Check if the application is running as a compiled executable (e.g., using PyInstaller)
                application_path = sys._MEIPASS  # Get the path to the temporary folder where assets are stored
                
            else:
                # If running as a script, get the directory of the current file
                application_path = os.path.dirname(os.path.abspath(__file__))
                
            # Construct the path to the icon file
            icon_path = os.path.join(application_path, 'assets', 'icon.ico')
            
            # Check if the icon file exists before trying to set it
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)  # Set the window icon to the specified file
            
        except Exception as e:
            print(f"Could not load application icon: {e}")  # Print error if icon loading fails
        
        # Initialize the GUI by creating an instance of FileOrganizerGUI with the main window as a parameter
        app = FileOrganizerGUI(root)
        
        # Start the application's main event loop, which waits for user interaction
        root.mainloop()
        
    except Exception as e:
        # If any exception occurs during setup or execution, show an error message box to the user
        tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")
        raise  # Re-raise the exception for further handling (if needed)

# Check if this script is being run directly (not imported as a module)
if __name__ == "__main__":
    main()  # Call the main function to start the application
