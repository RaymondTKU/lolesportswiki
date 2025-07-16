from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.database import get_db
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/comments', methods=['POST'])
@jwt_required()
def create_comment():
    """建立留言"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # 驗證必要欄位
        if not data.get('content') or not data.get('match_id'):
            return jsonify({
                'success': False,
                'message': '請提供留言內容和賽事ID'
            }), 400
        
        # 驗證留言內容長度
        if len(data['content']) > 500:
            return jsonify({
                'success': False,
                'message': '留言內容不能超過500字'
            }), 400
        
        db = get_db()
        
        # 確認使用者存在
        user = db.users.find_one({'_id': ObjectId(current_user_id)})
        if not user:
            return jsonify({
                'success': False,
                'message': '使用者不存在'
            }), 404
        
        # 確認賽事存在
        match = db.matches.find_one({'_id': ObjectId(data['match_id'])})
        if not match:
            return jsonify({
                'success': False,
                'message': '賽事不存在'
            }), 404
        
        # 建立留言
        comment = {
            'content': data['content'].strip(),
            'user_id': ObjectId(current_user_id),
            'match_id': ObjectId(data['match_id']),
            'created_at': datetime.utcnow(),
            'likes': 0,
            'replies': []
        }
        
        result = db.comments.insert_one(comment)
        
        # 取得完整留言資料（包含使用者資訊）
        comment_with_user = db.comments.aggregate([
            {'$match': {'_id': result.inserted_id}},
            {'$lookup': {
                'from': 'users',
                'localField': 'user_id',
                'foreignField': '_id',
                'as': 'user'
            }},
            {'$unwind': '$user'},
            {'$project': {
                'content': 1,
                'created_at': 1,
                'likes': 1,
                'user.username': 1,
                'user.avatar': 1
            }}
        ]).next()
        
        # 轉換ObjectId為字串
        comment_with_user['id'] = str(comment_with_user['_id'])
        comment_with_user['user']['id'] = str(comment_with_user['user']['_id'])
        del comment_with_user['_id']
        del comment_with_user['user']['_id']
        
        return jsonify({
            'success': True,
            'message': '留言發表成功',
            'data': comment_with_user
        }), 201
        
    except Exception as e:
        logger.error(f"建立留言失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '建立留言失敗'
        }), 500

@comments_bp.route('/comments/match/<match_id>', methods=['GET'])
def get_match_comments(match_id):
    """取得賽事留言"""
    try:
        # 驗證賽事ID格式
        if not ObjectId.is_valid(match_id):
            return jsonify({
                'success': False,
                'message': '無效的賽事ID'
            }), 400
        
        db = get_db()
        
        # 確認賽事存在
        match = db.matches.find_one({'_id': ObjectId(match_id)})
        if not match:
            return jsonify({
                'success': False,
                'message': '賽事不存在'
            }), 404
        
        # 取得分頁參數
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit
        
        # 取得留言（包含使用者資訊）
        comments = list(db.comments.aggregate([
            {'$match': {'match_id': ObjectId(match_id)}},
            {'$lookup': {
                'from': 'users',
                'localField': 'user_id',
                'foreignField': '_id',
                'as': 'user'
            }},
            {'$unwind': '$user'},
            {'$sort': {'created_at': -1}},
            {'$skip': skip},
            {'$limit': limit},
            {'$project': {
                'content': 1,
                'created_at': 1,
                'likes': 1,
                'user.username': 1,
                'user.avatar': 1
            }}
        ]))
        
        # 取得總留言數
        total_comments = db.comments.count_documents({'match_id': ObjectId(match_id)})
        
        # 轉換ObjectId為字串
        for comment in comments:
            comment['id'] = str(comment['_id'])
            comment['user']['id'] = str(comment['user']['_id'])
            del comment['_id']
            del comment['user']['_id']
        
        return jsonify({
            'success': True,
            'data': comments,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_comments,
                'total_pages': (total_comments + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        logger.error(f"取得留言失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '取得留言失敗'
        }), 500

@comments_bp.route('/comments/<comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """刪除留言"""
    try:
        # 驗證留言ID格式
        if not ObjectId.is_valid(comment_id):
            return jsonify({
                'success': False,
                'message': '無效的留言ID'
            }), 400
        
        current_user_id = get_jwt_identity()
        db = get_db()
        
        # 確認留言存在
        comment = db.comments.find_one({'_id': ObjectId(comment_id)})
        if not comment:
            return jsonify({
                'success': False,
                'message': '留言不存在'
            }), 404
        
        # 確認是留言作者或管理員
        current_user = db.users.find_one({'_id': ObjectId(current_user_id)})
        if str(comment['user_id']) != current_user_id and current_user.get('role') != 'admin':
            return jsonify({
                'success': False,
                'message': '沒有權限刪除此留言'
            }), 403
        
        # 刪除留言
        db.comments.delete_one({'_id': ObjectId(comment_id)})
        
        return jsonify({
            'success': True,
            'message': '留言已刪除'
        }), 200
        
    except Exception as e:
        logger.error(f"刪除留言失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '刪除留言失敗'
        }), 500

@comments_bp.route('/comments/<comment_id>/like', methods=['POST'])
@jwt_required()
def like_comment(comment_id):
    """按讚留言"""
    try:
        # 驗證留言ID格式
        if not ObjectId.is_valid(comment_id):
            return jsonify({
                'success': False,
                'message': '無效的留言ID'
            }), 400
        
        current_user_id = get_jwt_identity()
        db = get_db()
        
        # 確認留言存在
        comment = db.comments.find_one({'_id': ObjectId(comment_id)})
        if not comment:
            return jsonify({
                'success': False,
                'message': '留言不存在'
            }), 404
        
        # 檢查是否已按讚
        like_record = db.comment_likes.find_one({
            'comment_id': ObjectId(comment_id),
            'user_id': ObjectId(current_user_id)
        })
        
        if like_record:
            # 取消按讚
            db.comment_likes.delete_one({
                'comment_id': ObjectId(comment_id),
                'user_id': ObjectId(current_user_id)
            })
            db.comments.update_one(
                {'_id': ObjectId(comment_id)},
                {'$inc': {'likes': -1}}
            )
            liked = False
        else:
            # 按讚
            db.comment_likes.insert_one({
                'comment_id': ObjectId(comment_id),
                'user_id': ObjectId(current_user_id),
                'created_at': datetime.utcnow()
            })
            db.comments.update_one(
                {'_id': ObjectId(comment_id)},
                {'$inc': {'likes': 1}}
            )
            liked = True
        
        # 取得最新按讚數
        updated_comment = db.comments.find_one({'_id': ObjectId(comment_id)})
        
        return jsonify({
            'success': True,
            'data': {
                'liked': liked,
                'likes': updated_comment['likes']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"按讚留言失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '按讚失敗'
        }), 500
