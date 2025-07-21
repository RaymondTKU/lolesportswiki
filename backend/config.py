import os
from datetime import timedelta
from pymongo import MongoClient

class Config:
    """基本配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'lol-esports-secret-key-2024'
    MONGODB_URI = os.environ.get('MONGO_URI') or os.environ.get('MONGODB_URI') or 'mongodb://mongo:27017/lolesportswiki_dev'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-2024'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True
    MONGODB_URI = 'mongodb://mongo:27017/lolesportswiki_dev'

class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False
    MONGODB_URI = os.environ.get('MONGO_URI') or os.environ.get('MONGODB_URI') or 'mongodb://mongo:27017/lolesportswiki'

class TestingConfig(Config):
    """測試環境配置"""
    TESTING = True
    MONGODB_URI = 'mongodb://mongo:27017/lolesportswiki_test'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# 資料庫連接函數
def get_database():
    """獲取資料庫連接"""
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    mongodb_uri = config[config_name].MONGODB_URI
    client = MongoClient(mongodb_uri)
    db_name = mongodb_uri.split('/')[-1]
    return client[db_name]
