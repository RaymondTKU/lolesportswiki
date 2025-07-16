from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import db
from models.user import User
from models.team import Team
from models.player import Player
from models.match import Match
from bson import ObjectId
import logging

admin_bp = Blueprint('admin', __name__)

def require_admin():
    """檢查是否為管理員"""
    current_user_id = get_jwt_identity()
    if not current_user_id:
        return jsonify({'message': '需要登入'}), 401
    
    user = User.find_by_id(current_user_id)
    if not user or user.get('role') != 'admin':
        return jsonify({'message': '需要管理員權限'}), 403
    
    return None

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """管理員控制台統計資料"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        # 統計資料
        stats = {
            'users': db.users.count_documents({}),
            'teams': db.teams.count_documents({}),
            'players': db.players.count_documents({}),
            'matches': db.matches.count_documents({}),
            'comments': db.comments.count_documents({}),
            'favorites': db.favorites.count_documents({})
        }
        
        # 最近活動
        recent_activities = []
        
        # 最近註冊的用戶
        recent_users = list(db.users.find({}, {'username': 1, 'email': 1, 'created_at': 1})
                           .sort('created_at', -1).limit(5))
        for user in recent_users:
            recent_activities.append({
                'type': 'user_register',
                'description': f'用戶 {user["username"]} 註冊',
                'timestamp': user.get('created_at', '')
            })
        
        # 最近的比賽
        recent_matches = list(db.matches.find({}, {'team_a': 1, 'team_b': 1, 'date': 1, 'status': 1})
                             .sort('date', -1).limit(5))
        for match in recent_matches:
            recent_activities.append({
                'type': 'match_created',
                'description': f'比賽 {match["team_a"]} vs {match["team_b"]}',
                'timestamp': match.get('date', '')
            })
        
        # 按時間排序
        recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'stats': stats,
            'recent_activities': recent_activities[:10]
        })
        
    except Exception as e:
        logging.error(f"獲取控制台資料失敗: {str(e)}")
        return jsonify({'message': '獲取控制台資料失敗'}), 500

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """獲取用戶列表"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        search = request.args.get('search', '')
        
        # 建立查詢條件
        query = {}
        if search:
            query = {
                '$or': [
                    {'username': {'$regex': search, '$options': 'i'}},
                    {'email': {'$regex': search, '$options': 'i'}}
                ]
            }
        
        # 計算總數
        total = db.users.count_documents(query)
        
        # 獲取用戶列表
        users = list(db.users.find(query, {'password': 0})
                    .sort('created_at', -1)
                    .skip((page - 1) * per_page)
                    .limit(per_page))
        
        # 轉換 ObjectId
        for user in users:
            user['_id'] = str(user['_id'])
        
        return jsonify({
            'users': users,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
        
    except Exception as e:
        logging.error(f"獲取用戶列表失敗: {str(e)}")
        return jsonify({'message': '獲取用戶列表失敗'}), 500

@admin_bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """更新用戶資料"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        data = request.get_json()
        
        # 驗證用戶存在
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({'message': '用戶不存在'}), 404
        
        # 更新資料
        update_data = {}
        if 'username' in data:
            update_data['username'] = data['username']
        if 'email' in data:
            update_data['email'] = data['email']
        if 'role' in data:
            update_data['role'] = data['role']
        if 'status' in data:
            update_data['status'] = data['status']
        
        # 執行更新
        result = db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        
        if result.modified_count:
            return jsonify({'message': '用戶資料更新成功'})
        else:
            return jsonify({'message': '沒有資料需要更新'}), 400
            
    except Exception as e:
        logging.error(f"更新用戶資料失敗: {str(e)}")
        return jsonify({'message': '更新用戶資料失敗'}), 500

@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """刪除用戶"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        # 驗證用戶存在
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({'message': '用戶不存在'}), 404
        
        # 不能刪除管理員帳號
        if user.get('role') == 'admin':
            return jsonify({'message': '不能刪除管理員帳號'}), 403
        
        # 刪除用戶相關資料
        db.comments.delete_many({'user_id': ObjectId(user_id)})
        db.favorites.delete_many({'user_id': ObjectId(user_id)})
        
        # 刪除用戶
        result = db.users.delete_one({'_id': ObjectId(user_id)})
        
        if result.deleted_count:
            return jsonify({'message': '用戶刪除成功'})
        else:
            return jsonify({'message': '刪除用戶失敗'}), 400
            
    except Exception as e:
        logging.error(f"刪除用戶失敗: {str(e)}")
        return jsonify({'message': '刪除用戶失敗'}), 500

@admin_bp.route('/matches', methods=['GET'])
@jwt_required()
def get_admin_matches():
    """獲取比賽列表（管理員）"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        search = request.args.get('search', '')
        
        # 建立查詢條件
        query = {}
        if search:
            query = {
                '$or': [
                    {'team_a': {'$regex': search, '$options': 'i'}},
                    {'team_b': {'$regex': search, '$options': 'i'}},
                    {'tournament': {'$regex': search, '$options': 'i'}}
                ]
            }
        
        # 計算總數
        total = db.matches.count_documents(query)
        
        # 獲取比賽列表
        matches = list(db.matches.find(query)
                      .sort('date', -1)
                      .skip((page - 1) * per_page)
                      .limit(per_page))
        
        # 轉換 ObjectId
        for match in matches:
            match['_id'] = str(match['_id'])
        
        return jsonify({
            'matches': matches,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
        
    except Exception as e:
        logging.error(f"獲取比賽列表失敗: {str(e)}")
        return jsonify({'message': '獲取比賽列表失敗'}), 500

@admin_bp.route('/matches/<match_id>', methods=['DELETE'])
@jwt_required()
def delete_match(match_id):
    """刪除比賽"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        # 驗證比賽存在
        match = db.matches.find_one({'_id': ObjectId(match_id)})
        if not match:
            return jsonify({'message': '比賽不存在'}), 404
        
        # 刪除比賽相關資料
        db.comments.delete_many({'match_id': ObjectId(match_id)})
        db.favorites.delete_many({'target_id': ObjectId(match_id), 'type': 'match'})
        
        # 刪除比賽
        result = db.matches.delete_one({'_id': ObjectId(match_id)})
        
        if result.deleted_count:
            return jsonify({'message': '比賽刪除成功'})
        else:
            return jsonify({'message': '刪除比賽失敗'}), 400
            
    except Exception as e:
        logging.error(f"刪除比賽失敗: {str(e)}")
        return jsonify({'message': '刪除比賽失敗'}), 500

@admin_bp.route('/comments', methods=['GET'])
@jwt_required()
def get_admin_comments():
    """獲取評論列表（管理員）"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # 計算總數
        total = db.comments.count_documents({})
        
        # 獲取評論列表
        comments = list(db.comments.aggregate([
            {
                '$lookup': {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': '_id',
                    'as': 'user'
                }
            },
            {
                '$lookup': {
                    'from': 'matches',
                    'localField': 'match_id',
                    'foreignField': '_id',
                    'as': 'match'
                }
            },
            {
                '$project': {
                    'content': 1,
                    'created_at': 1,
                    'likes': 1,
                    'user.username': 1,
                    'match.team_a': 1,
                    'match.team_b': 1
                }
            },
            {'$sort': {'created_at': -1}},
            {'$skip': (page - 1) * per_page},
            {'$limit': per_page}
        ]))
        
        # 轉換 ObjectId
        for comment in comments:
            comment['_id'] = str(comment['_id'])
            comment['user'] = comment['user'][0] if comment['user'] else None
            comment['match'] = comment['match'][0] if comment['match'] else None
        
        return jsonify({
            'comments': comments,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
        
    except Exception as e:
        logging.error(f"獲取評論列表失敗: {str(e)}")
        return jsonify({'message': '獲取評論列表失敗'}), 500

@admin_bp.route('/comments/<comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """刪除評論"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    try:
        # 驗證評論存在
        comment = db.comments.find_one({'_id': ObjectId(comment_id)})
        if not comment:
            return jsonify({'message': '評論不存在'}), 404
        
        # 刪除評論
        result = db.comments.delete_one({'_id': ObjectId(comment_id)})
        
        if result.deleted_count:
            return jsonify({'message': '評論刪除成功'})
        else:
            return jsonify({'message': '刪除評論失敗'}), 400
            
    except Exception as e:
        logging.error(f"刪除評論失敗: {str(e)}")
        return jsonify({'message': '刪除評論失敗'}), 500
