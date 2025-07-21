from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import jwt
from functools import wraps
from ..models.user import User
from ..config import Config

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    """JWT Token 驗證裝飾器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 從 Authorization header 中獲取 token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Token 格式錯誤'}), 401
        
        if not token:
            return jsonify({'message': '缺少認證 token'}), 401
        
        try:
            # 解碼 token
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            current_user = User.find_by_id(data['user_id'])
            if not current_user:
                return jsonify({'message': '無效的 token'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token 已過期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '無效的 token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    """使用者註冊"""
    try:
        data = request.get_json()
        
        # 驗證必要欄位
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'message': '缺少必要欄位'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # 驗證用戶名格式
        if not User.validate_username(username):
            return jsonify({'message': '用戶名格式不正確（3-20字符，只能包含字母、數字和下底線）'}), 400
        
        # 驗證電子郵件格式
        if not User.validate_email(email):
            return jsonify({'message': '電子郵件格式不正確'}), 400
        
        # 驗證密碼強度
        if not User.validate_password(password):
            return jsonify({'message': '密碼至少需要6個字符'}), 400
        
        # 檢查用戶名是否已存在
        if User.find_by_username(username):
            return jsonify({'message': '用戶名已存在'}), 409
        
        # 檢查電子郵件是否已存在
        if User.find_by_email(email):
            return jsonify({'message': '電子郵件已被註冊'}), 409
        
        # 創建新使用者
        user = User(username=username, email=email, password=password)
        user_id = user.save()
        
        if user_id:
            # 生成 JWT token
            token = jwt.encode({
                'user_id': user_id,
                'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES
            }, Config.JWT_SECRET_KEY, algorithm='HS256')
            
            return jsonify({
                'message': '註冊成功',
                'token': token,
                'user': user.to_dict()
            }), 201
        else:
            return jsonify({'message': '註冊失敗'}), 500
            
    except Exception as e:
        print(e, flush=True)
        return jsonify({'message': f'伺服器錯誤: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """使用者登入"""
    try:
        data = request.get_json()
        
        # 驗證必要欄位
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': '缺少用戶名或密碼'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # 查找使用者（支援用戶名或電子郵件登入）
        user = User.find_by_username(username)
        if not user:
            user = User.find_by_email(username)
        
        if not user or not user.check_password(password):
            return jsonify({'message': '用戶名或密碼錯誤'}), 401
        
        if not user.is_active:
            return jsonify({'message': '帳戶已被停用'}), 401
        
        # 生成 JWT token
        token = jwt.encode({
            'user_id': str(user._id),
            'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES
        }, Config.JWT_SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'message': '登入成功',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'伺服器錯誤: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """取得當前使用者資訊"""
    try:
        return jsonify({
            'user': current_user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'message': f'伺服器錯誤: {str(e)}'}), 500

@auth_bp.route('/me', methods=['PUT'])
@token_required
def update_current_user(current_user):
    """更新當前使用者資訊"""
    try:
        data = request.get_json()
        
        # 更新個人資料
        if 'profile' in data:
            profile = data['profile']
            if 'display_name' in profile:
                current_user.profile['display_name'] = profile['display_name']
            if 'bio' in profile:
                current_user.profile['bio'] = profile['bio']
            if 'favorite_team' in profile:
                current_user.profile['favorite_team'] = profile['favorite_team']
            if 'favorite_player' in profile:
                current_user.profile['favorite_player'] = profile['favorite_player']
        
        # 更新到資料庫
        current_user.updated_at = datetime.utcnow()
        collection = db.get_db().users
        collection.update_one(
            {'_id': current_user._id},
            {'$set': {
                'profile': current_user.profile,
                'updated_at': current_user.updated_at
            }}
        )
        
        return jsonify({
            'message': '更新成功',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'伺服器錯誤: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """使用者登出"""
    # 在實際應用中，你可能想要將 token 加入黑名單
    # 目前只是返回成功訊息
    return jsonify({'message': '登出成功'}), 200
