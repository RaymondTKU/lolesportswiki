#!/usr/bin/env python3
"""
管理員帳號初始化腳本
運行此腳本創建默認管理員帳號
"""

import os
import sys
from datetime import datetime

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from models.database import db
from models.user import User

def init_admin():
    """初始化管理員帳號"""
    try:
        # 連接資料庫
        app_config = config['default']
        if not db.connect(app_config.MONGODB_URI):
            print("❌ 資料庫連接失敗")
            return False
        
        # 檢查是否已有管理員
        existing_admin = db.users.find_one({'role': 'admin'})
        if existing_admin:
            print("✅ 管理員帳號已存在")
            print(f"   用戶名: {existing_admin['username']}")
            print(f"   電子郵件: {existing_admin['email']}")
            return True
        
        # 創建默認管理員帳號
        admin_data = {
            'username': 'admin',
            'email': 'admin@lolesportswiki.com',
            'password_hash': User.generate_password_hash('admin123'),
            'role': 'admin',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True,
            'favorites': [],
            'profile': {
                'display_name': 'Administrator',
                'bio': '系統管理員',
                'avatar': '',
                'favorite_team': '',
                'favorite_player': ''
            }
        }
        
        result = db.users.insert_one(admin_data)
        
        if result.inserted_id:
            print("✅ 管理員帳號創建成功")
            print("   用戶名: admin")
            print("   密碼: admin123")
            print("   電子郵件: admin@lolesportswiki.com")
            print("   ⚠️  請登入後立即修改密碼")
            return True
        else:
            print("❌ 管理員帳號創建失敗")
            return False
            
    except Exception as e:
        print(f"❌ 初始化管理員帳號失敗: {str(e)}")
        return False

def create_sample_data():
    """創建示例數據"""
    try:
        # 創建示例隊伍
        sample_teams = [
            {
                'name': 'T1',
                'region': 'LCK',
                'logo': '/images/teams/t1.png',
                'founded': 2013,
                'description': '韓國頂級電競俱樂部，英雄聯盟世界冠軍',
                'achievements': ['2023 世界冠軍', '2022 世界冠軍', '2021 世界冠軍'],
                'social_links': {
                    'twitter': '@T1LoL',
                    'instagram': '@t1lol',
                    'youtube': 'T1LoL'
                },
                'roster': [],
                'stats': {
                    'wins': 0,
                    'losses': 0,
                    'win_rate': 0.0
                },
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'name': 'Gen.G',
                'region': 'LCK',
                'logo': '/images/teams/geng.png',
                'founded': 2017,
                'description': '韓國電競俱樂部，LCK強隊',
                'achievements': ['2024 春季賽冠軍', '2023 夏季賽冠軍'],
                'social_links': {
                    'twitter': '@GenG_esports',
                    'instagram': '@geng_esports',
                    'youtube': 'GenGesports'
                },
                'roster': [],
                'stats': {
                    'wins': 0,
                    'losses': 0,
                    'win_rate': 0.0
                },
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'name': 'JDG',
                'region': 'LPL',
                'logo': '/images/teams/jdg.png',
                'founded': 2017,
                'description': '中國電競俱樂部，LPL強隊',
                'achievements': ['2023 春季賽冠軍', '2022 世界四強'],
                'social_links': {
                    'twitter': '@JDGaming',
                    'instagram': '@jdgaming',
                    'youtube': 'JDGaming'
                },
                'roster': [],
                'stats': {
                    'wins': 0,
                    'losses': 0,
                    'win_rate': 0.0
                },
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        ]
        
        # 檢查是否已有隊伍數據
        if db.teams.count_documents({}) == 0:
            db.teams.insert_many(sample_teams)
            print("✅ 示例隊伍數據創建成功")
        else:
            print("✅ 隊伍數據已存在")
        
        # 創建示例選手
        sample_players = [
            {
                'nickname': 'Faker',
                'real_name': 'Lee Sang-hyeok',
                'position': 'Mid',
                'team': 'T1',
                'age': 27,
                'nationality': 'KR',
                'avatar': '/images/players/faker.png',
                'bio': '史上最偉大的英雄聯盟選手之一',
                'achievements': ['5次世界冠軍', '2次MSI冠軍', '10次LCK冠軍'],
                'social_links': {
                    'twitter': '@faker',
                    'instagram': '@faker',
                    'twitch': 'faker'
                },
                'stats': {
                    'kda': 2.5,
                    'win_rate': 0.75,
                    'games_played': 100
                },
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'nickname': 'Keria',
                'real_name': 'Ryu Min-seok',
                'position': 'Support',
                'team': 'T1',
                'age': 22,
                'nationality': 'KR',
                'avatar': '/images/players/keria.png',
                'bio': '頂級輔助選手',
                'achievements': ['3次世界冠軍', '1次MSI冠軍', '4次LCK冠軍'],
                'social_links': {
                    'twitter': '@keria',
                    'instagram': '@keria',
                    'twitch': 'keria'
                },
                'stats': {
                    'kda': 3.2,
                    'win_rate': 0.78,
                    'games_played': 95
                },
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        ]
        
        # 檢查是否已有選手數據
        if db.players.count_documents({}) == 0:
            db.players.insert_many(sample_players)
            print("✅ 示例選手數據創建成功")
        else:
            print("✅ 選手數據已存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 創建示例數據失敗: {str(e)}")
        return False

if __name__ == '__main__':
    print("🚀 初始化英雄聯盟電競資訊網...")
    print("=" * 50)
    
    # 初始化管理員帳號
    if init_admin():
        print("\n📊 創建示例數據...")
        create_sample_data()
        
        print("\n" + "=" * 50)
        print("✅ 初始化完成！")
        print("\n📋 管理員登入資訊:")
        print("   URL: http://localhost:5000/pages/admin.html")
        print("   用戶名: admin")
        print("   密碼: admin123")
        print("\n⚠️  請立即登入並修改管理員密碼！")
    else:
        print("\n❌ 初始化失敗")
        sys.exit(1)
