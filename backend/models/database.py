from pymongo import MongoClient
from datetime import datetime
import os

class Database:
    """資料庫連接管理"""
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def connect(self, uri):
        """連接到MongoDB"""
        try:
            self._client = MongoClient(uri)
            # 從URI中提取資料庫名稱
            db_name = uri.split('/')[-1]
            self._db = self._client[db_name]
            print(f"成功連接到資料庫: {db_name}")
            return True
        except Exception as e:
            print(f"資料庫連接失敗: {e}")
            return False
    
    def get_db(self):
        """取得資料庫實例"""
        return self._db
    
    def close(self):
        """關閉資料庫連接"""
        if self._client:
            self._client.close()

# 全域資料庫實例
db = Database()
