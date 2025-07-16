from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
import os
import sys

# 添加parent目錄到path以便import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.player import Player
from models.team import Team
from config import get_database

# 創建Blueprint
player_bp = Blueprint('players', __name__)

@player_bp.route('/players', methods=['GET'])
def get_players():
    """獲取選手列表"""
    try:
        db = get_database()
        
        # 獲取查詢參數
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        team_id = request.args.get('team_id')
        position = request.args.get('position')
        status = request.args.get('status')
        search = request.args.get('search')
        
        # 計算分頁
        skip = (page - 1) * per_page
        
        if search:
            # 搜索功能
            players = Player.search_by_nickname(db, search)
        else:
            # 一般列表查詢
            players = Player.find_all(db, skip=skip, limit=per_page, 
                                    team_id=team_id, position=position, status=status)
        
        # 轉換為JSON格式並添加隊伍資訊
        players_json = []
        for player in players:
            player_json = player.to_json()
            # 添加隊伍資訊
            if player.team_id:
                team_info = player.get_team_info(db)
                player_json['team'] = team_info
            players_json.append(player_json)
        
        # 計算總數（用於分頁）
        total_query = {}
        if team_id:
            total_query['team_id'] = team_id
        if position:
            total_query['position'] = position
        if status:
            total_query['status'] = status
        if search:
            total_query['nickname'] = {'$regex': search, '$options': 'i'}
        
        total_count = db.players.count_documents(total_query)
        
        return jsonify({
            'success': True,
            'data': players_json,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        print(f"獲取選手列表時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取選手列表失敗'
        }), 500

@player_bp.route('/players/<player_id>', methods=['GET'])
def get_player(player_id):
    """獲取單一選手詳情"""
    try:
        db = get_database()
        
        # 查找選手
        player = Player.find_by_id(db, player_id)
        if not player:
            return jsonify({
                'success': False,
                'message': '選手不存在'
            }), 404
        
        # 獲取選手資訊
        player_json = player.to_json()
        
        # 添加隊伍資訊
        if player.team_id:
            team_info = player.get_team_info(db)
            player_json['team'] = team_info
        
        return jsonify({
            'success': True,
            'data': player_json
        })
        
    except Exception as e:
        print(f"獲取選手詳情時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取選手詳情失敗'
        }), 500

@player_bp.route('/players', methods=['POST'])
@jwt_required()
def create_player():
    """創建新選手"""
    try:
        db = get_database()
        data = request.get_json()
        
        # 驗證必要欄位
        required_fields = ['nickname', 'real_name', 'position']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'缺少必要欄位: {field}'
                }), 400
        
        # 創建選手實例
        player = Player(
            nickname=data['nickname'],
            real_name=data['real_name'],
            position=data['position'],
            team_id=data.get('team_id'),
            avatar=data.get('avatar', ''),
            age=data.get('age'),
            nationality=data.get('nationality', ''),
            biography=data.get('biography', ''),
            social_media=data.get('social_media', {}),
            stats=data.get('stats', {}),
            achievements=data.get('achievements', []),
            status=data.get('status', 'active')
        )
        
        # 設定加入日期
        if 'join_date' in data:
            player.join_date = datetime.fromisoformat(data['join_date'])
        elif player.team_id:
            player.join_date = datetime.now()
        
        # 儲存到資料庫
        if player.save(db):
            # 如果有指定隊伍，更新隊伍成員列表
            if player.team_id:
                team = Team.find_by_id(db, player.team_id)
                if team:
                    team.add_member(db, str(player._id))
            
            return jsonify({
                'success': True,
                'message': '選手創建成功',
                'data': player.to_json()
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': '選手創建失敗'
            }), 500
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        print(f"創建選手時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '創建選手失敗'
        }), 500

@player_bp.route('/players/<player_id>', methods=['PUT'])
@jwt_required()
def update_player(player_id):
    """更新選手資訊"""
    try:
        db = get_database()
        data = request.get_json()
        
        # 查找選手
        player = Player.find_by_id(db, player_id)
        if not player:
            return jsonify({
                'success': False,
                'message': '選手不存在'
            }), 404
        
        # 更新欄位
        if 'nickname' in data:
            player.nickname = data['nickname']
        if 'real_name' in data:
            player.real_name = data['real_name']
        if 'position' in data:
            player.position = data['position']
        if 'avatar' in data:
            player.avatar = data['avatar']
        if 'age' in data:
            player.age = data['age']
        if 'nationality' in data:
            player.nationality = data['nationality']
        if 'biography' in data:
            player.biography = data['biography']
        if 'social_media' in data:
            player.social_media = data['social_media']
        if 'stats' in data:
            player.stats = data['stats']
        if 'achievements' in data:
            player.achievements = data['achievements']
        if 'status' in data:
            player.status = data['status']
        if 'join_date' in data:
            player.join_date = datetime.fromisoformat(data['join_date'])
        
        # 特殊處理隊伍變更
        if 'team_id' in data:
            new_team_id = data['team_id']
            if player.update_team(db, new_team_id):
                return jsonify({
                    'success': True,
                    'message': '選手隊伍更新成功',
                    'data': player.to_json()
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '選手隊伍更新失敗'
                }), 500
        
        # 儲存更新
        if player.save(db):
            return jsonify({
                'success': True,
                'message': '選手更新成功',
                'data': player.to_json()
            })
        else:
            return jsonify({
                'success': False,
                'message': '選手更新失敗'
            }), 500
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        print(f"更新選手時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新選手失敗'
        }), 500

@player_bp.route('/players/<player_id>', methods=['DELETE'])
@jwt_required()
def delete_player(player_id):
    """刪除選手"""
    try:
        db = get_database()
        
        # 查找選手
        player = Player.find_by_id(db, player_id)
        if not player:
            return jsonify({
                'success': False,
                'message': '選手不存在'
            }), 404
        
        # 如果選手有隊伍，從隊伍中移除
        if player.team_id:
            team = Team.find_by_id(db, player.team_id)
            if team:
                team.remove_member(db, player_id)
        
        # 刪除選手
        if player.delete(db):
            return jsonify({
                'success': True,
                'message': '選手刪除成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '選手刪除失敗'
            }), 500
            
    except Exception as e:
        print(f"刪除選手時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '刪除選手失敗'
        }), 500

@player_bp.route('/players/<player_id>/team', methods=['PUT'])
@jwt_required()
def update_player_team(player_id):
    """更新選手隊伍"""
    try:
        db = get_database()
        data = request.get_json()
        
        # 查找選手
        player = Player.find_by_id(db, player_id)
        if not player:
            return jsonify({
                'success': False,
                'message': '選手不存在'
            }), 404
        
        # 獲取新隊伍ID
        new_team_id = data.get('team_id')
        
        # 驗證新隊伍是否存在（如果不是None）
        if new_team_id:
            team = Team.find_by_id(db, new_team_id)
            if not team:
                return jsonify({
                    'success': False,
                    'message': '指定的隊伍不存在'
                }), 404
        
        # 更新隊伍
        if player.update_team(db, new_team_id):
            # 更新加入日期
            if new_team_id:
                player.join_date = datetime.now()
                player.save(db)
            
            return jsonify({
                'success': True,
                'message': '選手隊伍更新成功',
                'data': player.to_json()
            })
        else:
            return jsonify({
                'success': False,
                'message': '選手隊伍更新失敗'
            }), 500
            
    except Exception as e:
        print(f"更新選手隊伍時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新選手隊伍失敗'
        }), 500

@player_bp.route('/players/<player_id>/statistics', methods=['PUT'])
@jwt_required()
def update_player_statistics(player_id):
    """更新選手統計數據"""
    try:
        db = get_database()
        data = request.get_json()
        
        # 查找選手
        player = Player.find_by_id(db, player_id)
        if not player:
            return jsonify({
                'success': False,
                'message': '選手不存在'
            }), 404
        
        # 更新統計數據
        if 'stats' in data:
            if player.update_statistics(db, data['stats']):
                return jsonify({
                    'success': True,
                    'message': '統計數據更新成功',
                    'data': player.to_json()
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '統計數據更新失敗'
                }), 500
        else:
            return jsonify({
                'success': False,
                'message': '缺少統計數據'
            }), 400
            
    except Exception as e:
        print(f"更新選手統計數據時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新統計數據失敗'
        }), 500

@player_bp.route('/players/<player_id>/achievements', methods=['POST'])
@jwt_required()
def add_player_achievement(player_id):
    """新增選手成就"""
    try:
        db = get_database()
        data = request.get_json()
        
        # 查找選手
        player = Player.find_by_id(db, player_id)
        if not player:
            return jsonify({
                'success': False,
                'message': '選手不存在'
            }), 404
        
        # 新增成就
        if 'achievement' in data:
            if player.add_achievement(db, data['achievement']):
                return jsonify({
                    'success': True,
                    'message': '成就新增成功',
                    'data': player.to_json()
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '成就新增失敗'
                }), 500
        else:
            return jsonify({
                'success': False,
                'message': '缺少成就資訊'
            }), 400
            
    except Exception as e:
        print(f"新增選手成就時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '新增成就失敗'
        }), 500

@player_bp.route('/players/positions', methods=['GET'])
def get_player_positions():
    """獲取所有選手位置列表"""
    try:
        positions = ['top', 'jungle', 'mid', 'adc', 'support', 'coach', 'substitute']
        
        return jsonify({
            'success': True,
            'data': positions
        })
        
    except Exception as e:
        print(f"獲取位置列表時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取位置列表失敗'
        }), 500

@player_bp.route('/players/free-agents', methods=['GET'])
def get_free_agents():
    """獲取自由選手列表（沒有隊伍的選手）"""
    try:
        db = get_database()
        
        # 獲取查詢參數
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        position = request.args.get('position')
        
        # 計算分頁
        skip = (page - 1) * per_page
        
        # 查詢沒有隊伍的選手
        query = {
            '$or': [
                {'team_id': None},
                {'team_id': {'$exists': False}}
            ],
            'status': 'active'
        }
        
        if position:
            query['position'] = position
        
        cursor = db.players.find(query).skip(skip).limit(per_page)
        
        players = []
        for data in cursor:
            player = Player.from_dict(data)
            players.append(player.to_json())
        
        total_count = db.players.count_documents(query)
        
        return jsonify({
            'success': True,
            'data': players,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        print(f"獲取自由選手列表時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取自由選手列表失敗'
        }), 500
