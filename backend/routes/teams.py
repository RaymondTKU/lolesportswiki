from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
import os
import sys

# 添加parent目錄到path以便import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.team import Team
from models.player import Player
from config import get_database

# 創建Blueprint
team_bp = Blueprint('teams', __name__)

@team_bp.route('/teams', methods=['GET'])
def get_teams():
    """獲取隊伍列表"""
    try:
        db = get_database()
        
        # 獲取查詢參數
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        region = request.args.get('region')
        status = request.args.get('status')
        search = request.args.get('search')
        
        # 計算分頁
        skip = (page - 1) * per_page
        
        if search:
            # 搜索功能
            teams = Team.search_by_name(db, search)
        else:
            # 一般列表查詢
            teams = Team.find_all(db, skip=skip, limit=per_page, 
                                region=region, status=status)
        
        # 轉換為JSON格式
        teams_json = [team.to_json() for team in teams]
        
        # 計算總數（用於分頁）
        total_query = {}
        if region:
            total_query['region'] = region
        if status:
            total_query['status'] = status
        if search:
            total_query['name'] = {'$regex': search, '$options': 'i'}
        
        total_count = db.teams.count_documents(total_query)
        
        return jsonify({
            'success': True,
            'data': teams_json,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        print(f"獲取隊伍列表時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取隊伍列表失敗'
        }), 500

@team_bp.route('/teams/<team_id>', methods=['GET'])
def get_team(team_id):
    """獲取單一隊伍詳情"""
    try:
        db = get_database()
        
        # 查找隊伍
        team = Team.find_by_id(db, team_id)
        if not team:
            return jsonify({
                'success': False,
                'message': '隊伍不存在'
            }), 404
        
        # 獲取隊伍成員資訊
        team_json = team.to_json()
        
        # 查找隊伍成員
        players = Player.find_by_team(db, team_id)
        team_json['players'] = [player.to_json() for player in players]
        
        return jsonify({
            'success': True,
            'data': team_json
        })
        
    except Exception as e:
        print(f"獲取隊伍詳情時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取隊伍詳情失敗'
        }), 500

@team_bp.route('/teams', methods=['POST'])
@jwt_required()
def create_team():
    """創建新隊伍"""
    try:
        db = get_database()
        data = request.get_json()
        
        # 驗證必要欄位
        required_fields = ['name', 'region', 'founded_year']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'缺少必要欄位: {field}'
                }), 400
        
        # 創建隊伍實例
        team = Team(
            name=data['name'],
            logo=data.get('logo', ''),
            region=data['region'],
            founded_year=data['founded_year'],
            description=data.get('description', ''),
            social_media=data.get('social_media', {}),
            statistics=data.get('statistics', {}),
            status=data.get('status', 'active')
        )
        
        # 儲存到資料庫
        if team.save(db):
            return jsonify({
                'success': True,
                'message': '隊伍創建成功',
                'data': team.to_json()
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': '隊伍創建失敗'
            }), 500
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        print(f"創建隊伍時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '創建隊伍失敗'
        }), 500

@team_bp.route('/teams/<team_id>', methods=['PUT'])
@jwt_required()
def update_team(team_id):
    """更新隊伍資訊"""
    try:
        db = get_database()
        data = request.get_json()
        
        # 查找隊伍
        team = Team.find_by_id(db, team_id)
        if not team:
            return jsonify({
                'success': False,
                'message': '隊伍不存在'
            }), 404
        
        # 更新欄位
        if 'name' in data:
            team.name = data['name']
        if 'logo' in data:
            team.logo = data['logo']
        if 'region' in data:
            team.region = data['region']
        if 'founded_year' in data:
            team.founded_year = data['founded_year']
        if 'description' in data:
            team.description = data['description']
        if 'social_media' in data:
            team.social_media = data['social_media']
        if 'statistics' in data:
            team.statistics = data['statistics']
        if 'status' in data:
            team.status = data['status']
        
        # 儲存更新
        if team.save(db):
            return jsonify({
                'success': True,
                'message': '隊伍更新成功',
                'data': team.to_json()
            })
        else:
            return jsonify({
                'success': False,
                'message': '隊伍更新失敗'
            }), 500
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        print(f"更新隊伍時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新隊伍失敗'
        }), 500

@team_bp.route('/teams/<team_id>', methods=['DELETE'])
@jwt_required()
def delete_team(team_id):
    """刪除隊伍"""
    try:
        db = get_database()
        
        # 查找隊伍
        team = Team.find_by_id(db, team_id)
        if not team:
            return jsonify({
                'success': False,
                'message': '隊伍不存在'
            }), 404
        
        # 檢查是否有相關的選手
        players = Player.find_by_team(db, team_id)
        if players:
            return jsonify({
                'success': False,
                'message': '無法刪除隊伍，請先移除所有隊員'
            }), 400
        
        # 刪除隊伍
        if team.delete(db):
            return jsonify({
                'success': True,
                'message': '隊伍刪除成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '隊伍刪除失敗'
            }), 500
            
    except Exception as e:
        print(f"刪除隊伍時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '刪除隊伍失敗'
        }), 500

@team_bp.route('/teams/<team_id>/players', methods=['GET'])
def get_team_players(team_id):
    """獲取隊伍成員列表"""
    try:
        db = get_database()
        
        # 驗證隊伍是否存在
        team = Team.find_by_id(db, team_id)
        if not team:
            return jsonify({
                'success': False,
                'message': '隊伍不存在'
            }), 404
        
        # 獲取隊伍成員
        players = Player.find_by_team(db, team_id)
        players_json = [player.to_json() for player in players]
        
        return jsonify({
            'success': True,
            'data': players_json
        })
        
    except Exception as e:
        print(f"獲取隊伍成員時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取隊伍成員失敗'
        }), 500

@team_bp.route('/teams/<team_id>/statistics', methods=['PUT'])
@jwt_required()
def update_team_statistics(team_id):
    """更新隊伍統計數據"""
    try:
        db = get_database()
        data = request.get_json()
        
        # 查找隊伍
        team = Team.find_by_id(db, team_id)
        if not team:
            return jsonify({
                'success': False,
                'message': '隊伍不存在'
            }), 404
        
        # 更新統計數據
        if 'statistics' in data:
            if team.update_statistics(db, data['statistics']):
                return jsonify({
                    'success': True,
                    'message': '統計數據更新成功',
                    'data': team.to_json()
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
        print(f"更新隊伍統計數據時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新統計數據失敗'
        }), 500

@team_bp.route('/teams/regions', methods=['GET'])
def get_team_regions():
    """獲取所有隊伍地區列表"""
    try:
        db = get_database()
        
        # 獲取所有不重複的地區
        regions = db.teams.distinct('region')
        
        return jsonify({
            'success': True,
            'data': regions
        })
        
    except Exception as e:
        print(f"獲取地區列表時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取地區列表失敗'
        }), 500
