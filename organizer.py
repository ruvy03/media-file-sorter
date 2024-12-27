import os
from typing import Dict, List, Optional
from utils import safe_copy_file, generate_unique_filename

class FileOrganizer:
    def __init__(self):
        self.history: List[Dict] = []
        self.undo_stack: List[Dict] = []
        
    def organize_file(self, file_info: Dict, destination: str, new_name: Optional[str] = None) -> Dict:
        """
        Copy a file to its destination with optional renaming.
        Returns action dict for history tracking.
        """
        source_path = file_info['path']
        
        if new_name:
            filename = new_name
        else:
            filename = os.path.basename(source_path)
            
        dest_path = os.path.join(destination, filename)
        dest_path = generate_unique_filename(dest_path)
        
        action = {
            'type': 'copy',
            'source': source_path,
            'destination': dest_path,
            'timestamp': os.path.getmtime(source_path),
            'success': False
        }
        
        if safe_copy_file(source_path, dest_path):
            action['success'] = True
            self.history.append(action)
            self.undo_stack.clear()  # Clear redo stack when new action is performed
            
        return action
    
    def undo_last_action(self) -> Optional[Dict]:
        """Undo the last file operation."""
        if not self.history:
            return None
            
        action = self.history.pop()
        
        if action['type'] == 'copy':
            try:
                if os.path.exists(action['destination']):
                    os.remove(action['destination'])
                self.undo_stack.append(action)
                return action
            except Exception as e:
                print(f"Error undoing action: {e}")
                self.history.append(action)  # Put it back in history if undo fails
                return None
    
    def redo_last_action(self) -> Optional[Dict]:
        """Redo the last undone action."""
        if not self.undo_stack:
            return None
            
        action = self.undo_stack.pop()
        
        if action['type'] == 'copy':
            if safe_copy_file(action['source'], action['destination']):
                self.history.append(action)
                return action
            self.undo_stack.append(action)  # Put it back in undo stack if redo fails
            
        return None
    
    def get_history(self) -> List[Dict]:
        """Get the complete history of file operations."""
        return self.history