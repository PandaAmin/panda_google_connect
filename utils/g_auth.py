from datetime import datetime
from flask import current_app
from models.models import AppSetting , db
# from utils.g_auth import GoogleAuthManager

class GoogleAuthManager:
    _cache = {}
    _cache_timestamp = None
    CACHE_TIMEOUT = 300  # 5 minutes
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Get any setting from database"""
        if cls._is_cache_valid() and key in cls._cache:
            return cls._cache[key]
        
        with current_app.app_context():
            setting = AppSetting.query.filter_by(key=key).first()
            value = setting.value if setting else default
            
            cls._cache[key] = value
            cls._cache_timestamp = datetime.utcnow()
            
            return value
    
    @classmethod
    def set_setting(cls, key, value, description=None):
        """Set any setting in database"""
        with current_app.app_context():
            setting = AppSetting.query.filter_by(key=key).first()
            
            if setting:
                setting.value = value
                setting.updated_at = datetime.utcnow()
                if description:
                    setting.description = description
            else:
                setting = AppSetting(
                    key=key,
                    value=value,
                    description=description
                )
                db.session.add(setting)
            
            db.session.commit()
            cls._cache[key] = value
            cls._cache_timestamp = datetime.utcnow()
            
            return setting
    
    @classmethod
    def get_credentials(cls):
        """Get all Google OAuth credentials at once"""
        return {
            'client_id': cls.get_setting('GOOGLE_CLIENT_ID'),
            'client_secret': cls.get_setting('GOOGLE_CLIENT_SECRET'),
            'redirect_uri': cls.get_setting('GOOGLE_REDIRECT_URI')
        }
    
    @classmethod
    def is_configured(cls):
        """Check if Google OAuth is properly configured"""
        credentials = cls.get_credentials()
        return all([credentials['client_id'], credentials['client_secret'], credentials['redirect_uri']])
    
    @classmethod
    def update_credentials(cls, client_id, client_secret, redirect_uri):
        """Update all Google OAuth credentials at once"""
        cls.set_setting('GOOGLE_CLIENT_ID', client_id, 'Google OAuth Client ID')
        cls.set_setting('GOOGLE_CLIENT_SECRET', client_secret, 'Google OAuth Client Secret')
        cls.set_setting('GOOGLE_REDIRECT_URI', redirect_uri, 'Google OAuth Redirect URI')
        cls.clear_cache()
    
    @classmethod
    def _is_cache_valid(cls):
        if cls._cache_timestamp is None:
            return False
        elapsed = (datetime.utcnow() - cls._cache_timestamp).total_seconds()
        return elapsed < cls.CACHE_TIMEOUT
    
    @classmethod
    def clear_cache(cls):
        cls._cache = {}
        cls._cache_timestamp = None

def init_google_auth_settings():
    """Initialize default Google Auth settings in database"""
    default_settings = {
        'GOOGLE_CLIENT_ID': {
            'value': '',
            'description': 'Google OAuth Client ID'
        },
        'GOOGLE_CLIENT_SECRET': {
            'value': '',
            'description': 'Google OAuth Client Secret'
        },
        'GOOGLE_REDIRECT_URI': {
            'value': 'http://localhost:5000/auth/callback',
            'description': 'Google OAuth Redirect URI'
        }
    }
    
    for key, config in default_settings.items():
        if not AppSetting.query.filter_by(key=key).first():
            GoogleAuthManager.set_setting(
                key, 
                config['value'], 
                config['description']
            )
    
    print("Google Auth settings initialized")