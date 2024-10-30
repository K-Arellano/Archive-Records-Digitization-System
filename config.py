from datetime import timedelta
import os

class Config:
    SECRET_KEY = "ABCDEFG12345"
    TEMPLATES_AUTO_RELOAD = True
    SESSION_COOKIE_SAMESITE = "strict"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "strict"
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_DURATION = timedelta(days=1)
    
    CAPTCHA_ENABLE = True
    CAPTCHA_LENGTH = 6
    CAPTCHA_WIDTH = 180
    CAPTCHA_HEIGHT = 60
    
    # Make sure the path is correct for your deployment
    UPLOAD_FOLDER = os.path.realpath('app/upload_folder')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
