from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from .database import db
import re

class User:
    """使用者模型"""
    
    def __init__(self, username=None, email=None, password=None, role='user'):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password) if password else None
        self.role = role
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_active = True
        self.favorites = []
        self.profile = {
            'display_name': username,
            'bio': '',
            'avatar': '',
            'favorite_team': '',
            'favorite_player': ''
        }
    
    def save(self):
        """儲存使用者到資料庫"""
        try:
            collection = db.get_db().users
            user_data = {
                'username': self.username,
                'email': self.email,
                'password_hash': self.password_hash,
                'role': self.role,
                'created_at': self.created_at,
                'updated_at': self.updated_at,
                'is_active': self.is_active,
                'favorites': self.favorites,
                'profile': self.profile
            }
            result = collection.insert_one(user_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"儲存使用者失敗: {e}")
            return None
    
    def check_password(self, password):
        """驗證密碼"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'profile': self.profile
        }
    
    @staticmethod
    def find_by_username(username):
        """根據用戶名查找使用者"""
        try:
            collection = db.get_db().users
            user_data = collection.find_one({'username': username})
            if user_data:
                user = User()
                user.username = user_data['username']
                user.email = user_data['email']
                user.password_hash = user_data['password_hash']
                user.role = user_data['role']
                user.created_at = user_data['created_at']
                user.updated_at = user_data['updated_at']
                user.is_active = user_data['is_active']
                user.favorites = user_data.get('favorites', [])
                user.profile = user_data.get('profile', {})
                user._id = user_data['_id']
                return user
            return None
        except Exception as e:
            print(f"查找使用者失敗: {e}")
            return None
    
    @staticmethod
    def find_by_email(email):
        """根據電子郵件查找使用者"""
        try:
            collection = db.get_db().users
            user_data = collection.find_one({'email': email})
            if user_data:
                user = User()
                user.username = user_data['username']
                user.email = user_data['email']
                user.password_hash = user_data['password_hash']
                user.role = user_data['role']
                user.created_at = user_data['created_at']
                user.updated_at = user_data['updated_at']
                user.is_active = user_data['is_active']
                user.favorites = user_data.get('favorites', [])
                user.profile = user_data.get('profile', {})
                user._id = user_data['_id']
                return user
            return None
        except Exception as e:
            print(f"查找使用者失敗: {e}")
            return None
    
    @staticmethod
    def find_by_id(user_id):
        """根據ID查找使用者"""
        try:
            collection = db.get_db().users
            user_data = collection.find_one({'_id': ObjectId(user_id)})
            if user_data:
                user = User()
                user.username = user_data['username']
                user.email = user_data['email']
                user.password_hash = user_data['password_hash']
                user.role = user_data['role']
                user.created_at = user_data['created_at']
                user.updated_at = user_data['updated_at']
                user.is_active = user_data['is_active']
                user.favorites = user_data.get('favorites', [])
                user.profile = user_data.get('profile', {})
                user._id = user_data['_id']
                return user
            return None
        except Exception as e:
            print(f"查找使用者失敗: {e}")
            return None
    
    @staticmethod
    def validate_email(email):
        """驗證電子郵件格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_username(username):
        """驗證用戶名格式"""
        if not username or len(username) < 3 or len(username) > 20:
            return False
        pattern = r'^[a-zA-Z0-9_]+$'
        return re.match(pattern, username) is not None
    
    @staticmethod
    def validate_password(password):
        """驗證密碼強度"""
        if not password or len(password) < 6:
            return False
        return True
    
    @staticmethod
    def generate_password_hash(password):
        """生成密碼哈希"""
        return generate_password_hash(password)
