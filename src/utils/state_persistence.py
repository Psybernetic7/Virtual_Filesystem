from cryptography.fernet import Fernet
import base64
import os
import pickle
from datetime import datetime

class StatePersistence:
    """
    Handles encrypted persistence of filesystem state.
    Uses Fernet (symmetric encryption) to secure the data.
    """
    
    def __init__(self):
        """
        Initialize encryption system.
        Generates a new key if none exists, or loads existing key.
        """
        self.key_file = '.fs_key'
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.key)
        
        self.cipher_suite = Fernet(self.key)
    
    def save_state(self, filesystem, filepath: str) -> bool:
        """
        Save and encrypt filesystem state.
        
        Args:
            filesystem: The filesystem instance to save
            filepath: Where to save the encrypted state
        """
        try:
            # Get current user for the operation
            user = filesystem.user_manager.get_current_user()
            
            # Prepare state data
            state = {
                'root': filesystem.root,
                'current_path': filesystem.get_current_path(),
                'user_manager': filesystem.user_manager,
                'timestamp': datetime.now().isoformat()
            }
            
            # Serialize and encrypt
            serialized_state = pickle.dumps(state)
            encrypted_data = self.cipher_suite.encrypt(serialized_state)
            
            # Save to hidden file
            hidden_path = os.path.join(os.path.dirname(filepath) or '.',
                                     f'.{os.path.basename(filepath)}')
            with open(hidden_path, 'wb') as f:
                f.write(encrypted_data)
            
            filesystem.logger.log_operation(
                "SAVE_STATE", hidden_path, user.username, True,
                "State encrypted and saved"
            )
            return True
            
        except Exception as e:
            if hasattr(filesystem, 'logger'):
                filesystem.logger.log_operation(
                    "SAVE_STATE", filepath, user.username, False,
                    f"Error: {str(e)}"
                )
            return False
    
    def load_state(self, filesystem, filepath: str) -> bool:
        """
        Load and decrypt filesystem state.
        
        Args:
            filesystem: The filesystem instance to restore to
            filepath: Path to the encrypted state file
        """
        try:
            user = filesystem.user_manager.get_current_user()
            
            # Get path to hidden file
            hidden_path = os.path.join(os.path.dirname(filepath) or '.',
                                     f'.{os.path.basename(filepath)}')
            
            # Read and decrypt
            with open(hidden_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            state = pickle.loads(decrypted_data)
            
            # Restore state
            filesystem.root = state['root']
            filesystem.user_manager = state['user_manager']
            
            # Restore current directory
            current_path = state['current_path']
            filesystem.current_directory = filesystem.get_node_by_path(current_path)
            if filesystem.current_directory is None:
                filesystem.current_directory = filesystem.root
            
            filesystem.logger.log_operation(
                "LOAD_STATE", hidden_path, user.username, True,
                f"State loaded from {state['timestamp']}"
            )
            return True
            
        except Exception as e:
            if hasattr(filesystem, 'logger'):
                filesystem.logger.log_operation(
                    "LOAD_STATE", filepath, user.username, False,
                    f"Error: {str(e)}"
                )
            return False