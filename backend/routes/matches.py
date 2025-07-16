from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime, timedelta
import os
import sys

# 添加parent目錄到path以便import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.match import Match
from models.team import Team
from config import get_database

# 創建Blueprint
match_bp = Blueprint('matches', __name__)

@match_bp.route('/matches', methods=['GET'])
def get_matches():
    """獲取比賽列表"""
    try:
        db = get_database()
        
        # 獲取查詢參數
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        tournament = request.args.get('tournament')
        season = request.args.get('season')
        status = request.args.get('status')
        team_id = request.args.get('team_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 計算分頁
        skip = (page - 1) * per_page
        
        # 處理日期篩選
        start_date_obj = None
        end_date_obj = None
        if start_date:
            start_date_obj = datetime.fromisoformat(start_date)
        if end_date:
            end_date_obj = datetime.fromisoformat(end_date)
        
        # 查詢比賽
        matches = Match.find_all(
            db, skip=skip, limit=per_page,
            tournament=tournament, season=season, status=status,
            team_id=team_id, start_date=start_date_obj, end_date=end_date_obj
        )
        
        # 轉換為JSON格式並添加隊伍資訊
        matches_json = []
        for match in matches:
            match_json = match.to_json()
            # 添加隊伍資訊
            teams_info = match.get_teams_info(db)
            match_json.update(teams_info)
            matches_json.append(match_json)
        
        # 計算總數（用於分頁）
        total_query = {}
        if tournament:
            total_query['tournament'] = {'$regex': tournament, '$options': 'i'}
        if season:
            total_query['season'] = season
        if status:
            total_query['status'] = status
        if team_id:
            total_query['$or'] = [
                {'team_a_id': team_id},
                {'team_b_id': team_id}
            ]
        if start_date_obj or end_date_obj:
            date_query = {}
            if start_date_obj:
                date_query['$gte'] = start_date_obj
            if end_date_obj:
                date_query['$lte'] = end_date_obj
            total_query['date'] = date_query
        
        total_count = db.matches.count_documents(total_query)
        
        return jsonify({
            'success': True,
            'data': matches_json,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        print(f"獲取比賽列表時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取比賽列表失敗'
        }), 500

@match_bp.route('/matches/<match_id>', methods=['GET'])
def get_match(match_id):
    """獲取單一比賽詳情"""
    try:
        db = get_database()
        
        # 查找比賽
        match = Match.find_by_id(db, match_id)
        if not match:
            return jsonify({
                'success': False,
                'message': '比賽不存在'
            }), 404
        
        # 獲取比賽資訊
        match_json = match.to_json()
        
        # 添加隊伍資訊
        teams_info = match.get_teams_info(db)
        match_json.update(teams_info)
        
        return jsonify({
            'success': True,
            'data': match_json
        })
        
    except Exception as e:
        print(f"獲取比賽詳情時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取比賽詳情失敗'
        }), 500

@match_bp.route('/matches', methods=['POST'])
@jwt_required()
def create_match():
    """創建新比賽"""
    try:
        db = get_database()
        data = request.get_json()
        
        # 驗證必要欄位
        required_fields = ['tournament', 'season', 'date', 'team_a_id', 'team_b_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'缺少必要欄位: {field}'
                }), 400
        
        # 驗證隊伍是否存在
        team_a = Team.find_by_id(db, data['team_a_id'])
        team_b = Team.find_by_id(db, data['team_b_id'])
        
        if not team_a:
            return jsonify({
                'success': False,
                'message': '隊伍A不存在'
            }), 400
        
        if not team_b:
            return jsonify({
                'success': False,
                'message': '隊伍B不存在'
            }), 400
        
        # 創建比賽實例
        match = Match(
            tournament=data['tournament'],
            season=data['season'],
            date=datetime.fromisoformat(data['date']),
            team_a_id=data['team_a_id'],
            team_b_id=data['team_b_id'],
            team_a_score=data.get('team_a_score', 0),
            team_b_score=data.get('team_b_score', 0),
            status=data.get('status', 'scheduled'),
            result=data.get('result'),
            match_format=data.get('match_format', 'BO3'),
            venue=data.get('venue', ''),
            stream_url=data.get('stream_url', ''),
            vod_url=data.get('vod_url', ''),
            notes=data.get('notes', ''),
            statistics=data.get('statistics', {}),
            game_details=data.get('game_details', [])
        )
        
        # 儲存到資料庫
        if match.save(db):
            return jsonify({
                'success': True,
                'message': '比賽創建成功',
                'data': match.to_json()
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': '比賽創建失敗'
            }), 500
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        print(f"創建比賽時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '創建比賽失敗'
        }), 500

@match_bp.route('/matches/<match_id>', methods=['PUT'])
@jwt_required()
def update_match(match_id):
    """更新比賽資訊"""
    try:
        db = get_database()
        data = request.get_json()
        
        # 查找比賽
        match = Match.find_by_id(db, match_id)
        if not match:
            return jsonify({
                'success': False,
                'message': '比賽不存在'
            }), 404
        
        # 更新欄位
        if 'tournament' in data:
            match.tournament = data['tournament']
        if 'season' in data:
            match.season = data['season']
        if 'date' in data:
            match.date = datetime.fromisoformat(data['date'])
        if 'team_a_id' in data:
            # 驗證隊伍是否存在
            team_a = Team.find_by_id(db, data['team_a_id'])
            if not team_a:
                return jsonify({
                    'success': False,
                    'message': '隊伍A不存在'
                }), 400
            match.team_a_id = data['team_a_id']
        if 'team_b_id' in data:
            # 驗證隊伍是否存在
            team_b = Team.find_by_id(db, data['team_b_id'])
            if not team_b:
                return jsonify({
                    'success': False,
                    'message': '隊伍B不存在'
                }), 400
            match.team_b_id = data['team_b_id']
        if 'team_a_score' in data:
            match.team_a_score = data['team_a_score']
        if 'team_b_score' in data:
            match.team_b_score = data['team_b_score']
        if 'status' in data:
            match.status = data['status']
        if 'result' in data:
            match.result = data['result']
        if 'match_format' in data:
            match.match_format = data['match_format']
        if 'venue' in data:
            match.venue = data['venue']
        if 'stream_url' in data:
            match.stream_url = data['stream_url']
        if 'vod_url' in data:
            match.vod_url = data['vod_url']
        if 'notes' in data:
            match.notes = data['notes']
        if 'statistics' in data:
            match.statistics = data['statistics']
        if 'game_details' in data:
            match.game_details = data['game_details']
        
        # 儲存更新
        if match.save(db):
            return jsonify({
                'success': True,
                'message': '比賽更新成功',
                'data': match.to_json()
            })
        else:
            return jsonify({
                'success': False,
                'message': '比賽更新失敗'
            }), 500
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        print(f"更新比賽時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新比賽失敗'
        }), 500

@match_bp.route('/matches/<match_id>', methods=['DELETE'])
@jwt_required()
def delete_match(match_id):
    """刪除比賽"""
    try:
        db = get_database()
        
        # 查找比賽
        match = Match.find_by_id(db, match_id)
        if not match:
            return jsonify({
                'success': False,
                'message': '比賽不存在'
            }), 404
        
        # 刪除比賽
        if match.delete(db):
            return jsonify({
                'success': True,
                'message': '比賽刪除成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '比賽刪除失敗'
            }), 500
            
    except Exception as e:
        print(f"刪除比賽時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '刪除比賽失敗'
        }), 500

@match_bp.route('/matches/<match_id>/score', methods=['PUT'])
@jwt_required()
def update_match_score(match_id):
    """更新比賽比分"""
    try:
        db = get_database()
        data = request.get_json()
        
        # 查找比賽
        match = Match.find_by_id(db, match_id)
        if not match:
            return jsonify({
                'success': False,
                'message': '比賽不存在'
            }), 404
        
        # 驗證必要欄位
        if 'team_a_score' not in data or 'team_b_score' not in data:
            return jsonify({
                'success': False,
                'message': '缺少比分資訊'
            }), 400
        
        # 更新比分
        if match.update_score(db, data['team_a_score'], data['team_b_score']):
            return jsonify({
                'success': True,
                'message': '比分更新成功',
                'data': match.to_json()
            })
        else:
            return jsonify({
                'success': False,
                'message': '比分更新失敗'
            }), 500
            
    except Exception as e:
        print(f"更新比分時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新比分失敗'
        }), 500

@match_bp.route('/matches/<match_id>/status', methods=['PUT'])
@jwt_required()
def update_match_status(match_id):
    """更新比賽狀態"""
    try:
        db = get_database()
        data = request.get_json()
        
        # 查找比賽
        match = Match.find_by_id(db, match_id)
        if not match:
            return jsonify({
                'success': False,
                'message': '比賽不存在'
            }), 404
        
        # 驗證必要欄位
        if 'status' not in data:
            return jsonify({
                'success': False,
                'message': '缺少狀態資訊'
            }), 400
        
        # 更新狀態
        if match.update_status(db, data['status']):
            return jsonify({
                'success': True,
                'message': '狀態更新成功',
                'data': match.to_json()
            })
        else:
            return jsonify({
                'success': False,
                'message': '狀態更新失敗'
            }), 500
            
    except Exception as e:
        print(f"更新狀態時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新狀態失敗'
        }), 500

@match_bp.route('/matches/upcoming', methods=['GET'])
def get_upcoming_matches():
    """獲取即將到來的比賽"""
    try:
        db = get_database()
        
        # 獲取查詢參數
        limit = int(request.args.get('limit', 10))
        
        # 查詢即將到來的比賽
        matches = Match.find_upcoming(db, limit=limit)
        
        # 轉換為JSON格式並添加隊伍資訊
        matches_json = []
        for match in matches:
            match_json = match.to_json()
            # 添加隊伍資訊
            teams_info = match.get_teams_info(db)
            match_json.update(teams_info)
            matches_json.append(match_json)
        
        return jsonify({
            'success': True,
            'data': matches_json
        })
        
    except Exception as e:
        print(f"獲取即將到來的比賽時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取即將到來的比賽失敗'
        }), 500

@match_bp.route('/matches/recent', methods=['GET'])
def get_recent_matches():
    """獲取最近的比賽"""
    try:
        db = get_database()
        
        # 獲取查詢參數
        limit = int(request.args.get('limit', 10))
        
        # 查詢最近的比賽
        matches = Match.find_recent(db, limit=limit)
        
        # 轉換為JSON格式並添加隊伍資訊
        matches_json = []
        for match in matches:
            match_json = match.to_json()
            # 添加隊伍資訊
            teams_info = match.get_teams_info(db)
            match_json.update(teams_info)
            matches_json.append(match_json)
        
        return jsonify({
            'success': True,
            'data': matches_json
        })
        
    except Exception as e:
        print(f"獲取最近比賽時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取最近比賽失敗'
        }), 500

@match_bp.route('/matches/live', methods=['GET'])
def get_live_matches():
    """獲取正在進行的比賽"""
    try:
        db = get_database()
        
        # 查詢正在進行的比賽
        matches = Match.find_all(db, status='live')
        
        # 轉換為JSON格式並添加隊伍資訊
        matches_json = []
        for match in matches:
            match_json = match.to_json()
            # 添加隊伍資訊
            teams_info = match.get_teams_info(db)
            match_json.update(teams_info)
            matches_json.append(match_json)
        
        return jsonify({
            'success': True,
            'data': matches_json
        })
        
    except Exception as e:
        print(f"獲取正在進行的比賽時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取正在進行的比賽失敗'
        }), 500

@match_bp.route('/matches/tournaments', methods=['GET'])
def get_tournaments():
    """獲取所有賽事名稱列表"""
    try:
        db = get_database()
        
        # 獲取所有不重複的賽事名稱
        tournaments = db.matches.distinct('tournament')
        
        return jsonify({
            'success': True,
            'data': tournaments
        })
        
    except Exception as e:
        print(f"獲取賽事列表時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取賽事列表失敗'
        }), 500

@match_bp.route('/matches/seasons', methods=['GET'])
def get_seasons():
    """獲取所有賽季列表"""
    try:
        db = get_database()
        
        # 獲取所有不重複的賽季
        seasons = db.matches.distinct('season')
        
        return jsonify({
            'success': True,
            'data': seasons
        })
        
    except Exception as e:
        print(f"獲取賽季列表時發生錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取賽季列表失敗'
        }), 500
