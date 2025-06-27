"""
User model for admin authentication
"""

from flask_login import UserMixin
from werkzeug.security import check_password_hash
import os

class User(UserMixin):
    """Simple user model for admin authentication"""
    
    def __init__(self, username):
        self.id = username
        self.username = username
    
    @staticmethod
    def verify_password(username, password):
        """Verify username and password against environment config"""
        from config import get_config
        config = get_config()
        
        # Check if credentials match
        if username == config.ADMIN_USERNAME:
            if config.ADMIN_PASSWORD_HASH:
                return check_password_hash(config.ADMIN_PASSWORD_HASH, password)
            # Development fallback - remove in production
            elif config.DEVELOPMENT_MODE and password == 'admin':
                return True
        return False
    
    @staticmethod
    def get(username):
        """Get user by username"""
        from config import get_config
        config = get_config()
        
        if username == config.ADMIN_USERNAME:
            return User(username)
        return None