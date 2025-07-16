#!/usr/bin/env python3
"""
API 測試腳本
用於測試英雄聯盟電競資訊網 API 功能
"""

import requests
import json
import time
from datetime import datetime

class APITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.token = None
        self.admin_token = None
        self.test_results = []
    
    def log_test(self, test_name, success, message=""):
        """記錄測試結果"""
        status = "✅" if success else "❌"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status} {test_name}: {message}")
    
    def make_request(self, method, endpoint, data=None, headers=None):
        """發送 HTTP 請求"""
        url = f"{self.base_url}{endpoint}"
        
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers, timeout=10)
            
            return response
        except requests.exceptions.RequestException as e:
            return None
    
    def test_health_check(self):
        """測試健康檢查"""
        response = self.make_request('GET', '/health')
        
        if response and response.status_code == 200:
            self.log_test("健康檢查", True, "API 服務正常運行")
            return True
        else:
            self.log_test("健康檢查", False, "API 服務無法訪問")
            return False
    
    def test_user_registration(self):
        """測試用戶註冊"""
        test_user = {
            'username': f'testuser_{int(time.time())}',
            'email': f'test_{int(time.time())}@example.com',
            'password': 'password123'
        }
        
        response = self.make_request('POST', '/api/auth/register', test_user)
        
        if response and response.status_code == 201:
            data = response.json()
            self.token = data.get('token')
            self.log_test("用戶註冊", True, f"成功註冊用戶: {test_user['username']}")
            return True
        else:
            self.log_test("用戶註冊", False, "註冊失敗")
            return False
    
    def test_user_login(self):
        """測試管理員登入"""
        admin_credentials = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = self.make_request('POST', '/api/auth/login', admin_credentials)
        
        if response and response.status_code == 200:
            data = response.json()
            self.admin_token = data.get('token')
            self.log_test("管理員登入", True, "管理員登入成功")
            return True
        else:
            self.log_test("管理員登入", False, "管理員登入失敗")
            return False
    
    def test_teams_api(self):
        """測試隊伍 API"""
        # 獲取隊伍列表
        response = self.make_request('GET', '/api/teams')
        
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("獲取隊伍列表", True, f"找到 {len(data.get('teams', []))} 支隊伍")
            return True
        else:
            self.log_test("獲取隊伍列表", False, "獲取隊伍列表失敗")
            return False
    
    def test_players_api(self):
        """測試選手 API"""
        # 獲取選手列表
        response = self.make_request('GET', '/api/players')
        
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("獲取選手列表", True, f"找到 {len(data.get('players', []))} 名選手")
            return True
        else:
            self.log_test("獲取選手列表", False, "獲取選手列表失敗")
            return False
    
    def test_matches_api(self):
        """測試比賽 API"""
        # 獲取比賽列表
        response = self.make_request('GET', '/api/matches')
        
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("獲取比賽列表", True, f"找到 {len(data.get('matches', []))} 場比賽")
            return True
        else:
            self.log_test("獲取比賽列表", False, "獲取比賽列表失敗")
            return False
    
    def test_favorites_api(self):
        """測試收藏 API"""
        if not self.token:
            self.log_test("測試收藏功能", False, "需要先登入")
            return False
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # 獲取收藏列表
        response = self.make_request('GET', '/api/favorites', headers=headers)
        
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("獲取收藏列表", True, f"找到 {len(data.get('favorites', []))} 個收藏")
            return True
        else:
            self.log_test("獲取收藏列表", False, "獲取收藏列表失敗")
            return False
    
    def test_comments_api(self):
        """測試評論 API"""
        if not self.token:
            self.log_test("測試評論功能", False, "需要先登入")
            return False
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # 創建測試評論
        test_comment = {
            'content': '這是一個測試評論',
            'match_id': '6536d6b2f1234567890abcde'  # 假設的比賽ID
        }
        
        response = self.make_request('POST', '/api/comments', test_comment, headers=headers)
        
        if response and response.status_code == 201:
            self.log_test("創建評論", True, "評論創建成功")
            return True
        else:
            self.log_test("創建評論", False, "評論創建失敗")
            return False
    
    def test_admin_api(self):
        """測試管理員 API"""
        if not self.admin_token:
            self.log_test("測試管理員功能", False, "需要先以管理員身份登入")
            return False
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # 獲取控制台資料
        response = self.make_request('GET', '/api/admin/dashboard', headers=headers)
        
        if response and response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            self.log_test("管理員控制台", True, f"系統統計: {stats}")
            return True
        else:
            self.log_test("管理員控制台", False, "獲取控制台資料失敗")
            return False
    
    def run_all_tests(self):
        """運行所有測試"""
        print("🚀 開始 API 測試...")
        print("=" * 60)
        
        # 基本連接測試
        if not self.test_health_check():
            print("❌ 基本連接測試失敗，終止測試")
            return
        
        # 用戶功能測試
        print("\n📝 用戶功能測試:")
        self.test_user_registration()
        self.test_user_login()
        
        # 核心功能測試
        print("\n⚽ 核心功能測試:")
        self.test_teams_api()
        self.test_players_api()
        self.test_matches_api()
        
        # 互動功能測試
        print("\n💬 互動功能測試:")
        self.test_favorites_api()
        self.test_comments_api()
        
        # 管理功能測試
        print("\n🔧 管理功能測試:")
        self.test_admin_api()
        
        # 測試結果統計
        print("\n" + "=" * 60)
        print("📊 測試結果統計:")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - successful_tests
        
        print(f"總測試數: {total_tests}")
        print(f"成功: {successful_tests}")
        print(f"失敗: {failed_tests}")
        print(f"成功率: {(successful_tests / total_tests * 100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失敗的測試:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "=" * 60)
        if failed_tests == 0:
            print("🎉 所有測試通過！系統運行正常。")
        else:
            print("⚠️  部分測試失敗，請檢查系統狀態。")
    
    def save_test_report(self, filename="test_report.json"):
        """保存測試報告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'total_tests': len(self.test_results),
            'successful_tests': sum(1 for result in self.test_results if result['success']),
            'failed_tests': sum(1 for result in self.test_results if not result['success']),
            'results': self.test_results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 測試報告已保存至: {filename}")

if __name__ == '__main__':
    print("🧪 英雄聯盟電競資訊網 API 測試工具")
    print("=" * 60)
    
    # 檢查是否提供了自訂 API 地址
    import sys
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    print(f"🔗 API 地址: {api_url}")
    print("⏳ 初始化測試...")
    
    tester = APITester(api_url)
    tester.run_all_tests()
    
    # 保存測試報告
    tester.save_test_report()
    
    print("\n✅ 測試完成！")
