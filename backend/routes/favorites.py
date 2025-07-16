from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.database import get_db
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

favorites_bp = Blueprint('favorites', __name__)

@favorites_bp.route('/favorites', methods=['POST'])
@jwt_required()
def add_favorite():
    """新增收藏"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # 驗證必要欄位
        if not data.get('type') or not data.get('target_id'):
            return jsonify({
                'success': False,
                'message': '請提供收藏類型和目標ID'
            }), 400
        
        # 驗證收藏類型
        valid_types = ['team', 'player', 'match']
        if data['type'] not in valid_types:
            return jsonify({
                'success': False,
                'message': f'收藏類型必須是: {", ".join(valid_types)}'
            }), 400
        
        # 驗證目標ID格式
        if not ObjectId.is_valid(data['target_id']):
            return jsonify({
                'success': False,
                'message': '無效的目標ID'
            }), 400
        
        db = get_db()
        
        # 確認目標存在
        collection_map = {
            'team': 'teams',
            'player': 'players',
            'match': 'matches'
        }
        
        target_collection = collection_map[data['type']]
        target = db[target_collection].find_one({'_id': ObjectId(data['target_id'])})
        if not target:
            return jsonify({
                'success': False,
                'message': f'{data["type"]} 不存在'
            }), 404
        
        # 檢查是否已收藏
        existing_favorite = db.favorites.find_one({
            'user_id': ObjectId(current_user_id),
            'type': data['type'],
            'target_id': ObjectId(data['target_id'])
        })
        
        if existing_favorite:
            return jsonify({
                'success': False,
                'message': '已經收藏過了'
            }), 400
        
        # 建立收藏
        favorite = {
            'user_id': ObjectId(current_user_id),
            'type': data['type'],
            'target_id': ObjectId(data['target_id']),
            'created_at': datetime.utcnow()
        }
        
        result = db.favorites.insert_one(favorite)
        
        return jsonify({
            'success': True,
            'message': '收藏成功',
            'data': {
                'id': str(result.inserted_id),
                'type': data['type'],
                'target_id': data['target_id']
            }
        }), 201
        
    except Exception as e:
        logger.error(f"新增收藏失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '新增收藏失敗'
        }), 500

@favorites_bp.route('/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    """取得收藏列表"""
    try:
        current_user_id = get_jwt_identity()
        db = get_db()
        
        # 取得篩選類型
        filter_type = request.args.get('type')
        
        # 建立查詢條件
        query = {'user_id': ObjectId(current_user_id)}
        if filter_type:
            query['type'] = filter_type
        
        # 取得分頁參數
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit
        
        # 取得收藏
        favorites = list(db.favorites.find(query)
                        .sort('created_at', -1)
                        .skip(skip)
                        .limit(limit))
        
        # 取得總數
        total_favorites = db.favorites.count_documents(query)
        
        # 填充目標資料
        enriched_favorites = []
        for favorite in favorites:
            collection_map = {
                'team': 'teams',
                'player': 'players',
                'match': 'matches'
            }
            
            target_collection = collection_map[favorite['type']]
            target = db[target_collection].find_one({'_id': favorite['target_id']})
            
            if target:
                # 轉換ObjectId為字串
                target['id'] = str(target['_id'])
                del target['_id']
                
                enriched_favorites.append({
                    'id': str(favorite['_id']),
                    'type': favorite['type'],
                    'target': target,
                    'created_at': favorite['created_at']
                })
        
        return jsonify({
            'success': True,
            'data': enriched_favorites,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_favorites,
                'total_pages': (total_favorites + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        logger.error(f"取得收藏失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '取得收藏失敗'
        }), 500

@favorites_bp.route('/favorites/<favorite_id>', methods=['DELETE'])
@jwt_required()
def remove_favorite(favorite_id):
    """移除收藏"""
    try:
        # 驗證收藏ID格式
        if not ObjectId.is_valid(favorite_id):
            return jsonify({
                'success': False,
                'message': '無效的收藏ID'
            }), 400
        
        current_user_id = get_jwt_identity()
        db = get_db()
        
        # 確認收藏存在且屬於當前使用者
        favorite = db.favorites.find_one({
            '_id': ObjectId(favorite_id),
            'user_id': ObjectId(current_user_id)
        })
        
        if not favorite:
            return jsonify({
                'success': False,
                'message': '收藏不存在'
            }), 404
        
        # 刪除收藏
        db.favorites.delete_one({'_id': ObjectId(favorite_id)})
        
        return jsonify({
            'success': True,
            'message': '已取消收藏'
        }), 200
        
    except Exception as e:
        logger.error(f"移除收藏失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '移除收藏失敗'
        }), 500

@favorites_bp.route('/favorites/check', methods=['POST'])
@jwt_required()
def check_favorite():
    """檢查是否已收藏"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # 驗證必要欄位
        if not data.get('type') or not data.get('target_id'):
            return jsonify({
                'success': False,
                'message': '請提供收藏類型和目標ID'
            }), 400
        
        # 驗證目標ID格式
        if not ObjectId.is_valid(data['target_id']):
            return jsonify({
                'success': False,
                'message': '無效的目標ID'
            }), 400
        
        db = get_db()
        
        # 檢查是否已收藏
        favorite = db.favorites.find_one({
            'user_id': ObjectId(current_user_id),
            'type': data['type'],
            'target_id': ObjectId(data['target_id'])
        })
        
        return jsonify({
            'success': True,
            'data': {
                'is_favorite': favorite is not None,
                'favorite_id': str(favorite['_id']) if favorite else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"檢查收藏狀態失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '檢查收藏狀態失敗'
        }), 500

@favorites_bp.route('/favorites/toggle', methods=['POST'])
@jwt_required()
def toggle_favorite():
    """切換收藏狀態"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # 驗證必要欄位
        if not data.get('type') or not data.get('target_id'):
            return jsonify({
                'success': False,
                'message': '請提供收藏類型和目標ID'
            }), 400
        
        # 驗證目標ID格式
        if not ObjectId.is_valid(data['target_id']):
            return jsonify({
                'success': False,
                'message': '無效的目標ID'
            }), 400
        
        db = get_db()
        
        # 檢查是否已收藏
        favorite = db.favorites.find_one({
            'user_id': ObjectId(current_user_id),
            'type': data['type'],
            'target_id': ObjectId(data['target_id'])
        })
        
        if favorite:
            # 移除收藏
            db.favorites.delete_one({'_id': favorite['_id']})
            is_favorite = False
            message = '已取消收藏'
        else:
            # 新增收藏
            favorite_data = {
                'user_id': ObjectId(current_user_id),
                'type': data['type'],
                'target_id': ObjectId(data['target_id']),
                'created_at': datetime.utcnow()
            }
            db.favorites.insert_one(favorite_data)
            is_favorite = True
            message = '收藏成功'
        
        return jsonify({
            'success': True,
            'message': message,
            'data': {
                'is_favorite': is_favorite
            }
        }), 200
        
    except Exception as e:
        logger.error(f"切換收藏狀態失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '切換收藏狀態失敗'
        }), 500
