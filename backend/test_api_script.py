# 英雄聯盟比賽資訊網 API 測試腳本
# 使用 requests 套件測試主要 API（需先安裝 requests）
import requests

BASE_URL = 'http://localhost:5000/api'

# 請先填入管理員帳號密碼
ADMIN_EMAIL = 'admin@example.com'
ADMIN_PASSWORD = 'your_admin_password'

def login():
    resp = requests.post(f'{BASE_URL}/auth/login', json={
        'email': ADMIN_EMAIL,
        'password': ADMIN_PASSWORD
    })
    data = resp.json()
    print('登入:', data)
    return data.get('token')

def test_create_match(token):
    headers = {'Authorization': f'Bearer {token}'}
    payload = {
        'tournament': 'LCK Summer',
        'season': '2025',
        'date': '2025-08-01',
        'team_a_id': 'teamA_id',
        'team_b_id': 'teamB_id',
        'status': 'scheduled',
        'match_format': 'BO3',
        'venue': 'Seoul',
        'notes': 'API 測試建立'
    }
    resp = requests.post(f'{BASE_URL}/matches', json=payload, headers=headers)
    print('建立比賽:', resp.json())
    return resp.json().get('data', {}).get('_id')

def test_get_matches():
    resp = requests.get(f'{BASE_URL}/matches')
    print('查詢比賽:', resp.json())

def test_update_match(token, match_id):
    headers = {'Authorization': f'Bearer {token}'}
    payload = {'notes': 'API 測試更新'}
    resp = requests.put(f'{BASE_URL}/matches/{match_id}', json=payload, headers=headers)
    print('更新比賽:', resp.json())

def test_delete_match(token, match_id):
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.delete(f'{BASE_URL}/matches/{match_id}', headers=headers)
    print('刪除比賽:', resp.json())

def main():
    token = login()
    if not token:
        print('登入失敗，請檢查帳密')
        return
    test_get_matches()
    match_id = test_create_match(token)
    if match_id:
        test_update_match(token, match_id)
        test_delete_match(token, match_id)
    test_get_matches()

if __name__ == '__main__':
    main()
