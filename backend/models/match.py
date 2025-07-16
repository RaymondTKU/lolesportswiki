from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from bson import ObjectId
from pymongo import MongoClient
import os

@dataclass
class Match:
    """比賽資料模型"""
    tournament: str
    season: str
    date: datetime
    team_a_id: str
    team_b_id: str
    team_a_score: int = 0
    team_b_score: int = 0
    status: str = "scheduled"  # scheduled, live, finished, cancelled
    result: Optional[str] = None  # win_a, win_b, draw
    match_format: str = "BO3"  # BO1, BO3, BO5
    venue: str = ""
    stream_url: str = ""
    vod_url: str = ""
    game_details: List[Dict[str, Any]] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    _id: Optional[ObjectId] = None

    def __post_init__(self):
        if isinstance(self.date, str):
            self.date = datetime.fromisoformat(self.date)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式用於MongoDB存儲"""
        data = {
            'tournament': self.tournament,
            'season': self.season,
            'date': self.date,
            'team_a_id': self.team_a_id,
            'team_b_id': self.team_b_id,
            'team_a_score': self.team_a_score,
            'team_b_score': self.team_b_score,
            'status': self.status,
            'result': self.result,
            'match_format': self.match_format,
            'venue': self.venue,
            'stream_url': self.stream_url,
            'vod_url': self.vod_url,
            'game_details': self.game_details,
            'statistics': self.statistics,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        if self._id:
            data['_id'] = self._id
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Match':
        """從字典創建Match實例"""
        match = cls(
            tournament=data['tournament'],
            season=data['season'],
            date=data['date'],
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
            game_details=data.get('game_details', []),
            statistics=data.get('statistics', {}),
            notes=data.get('notes', ''),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now())
        )
        if '_id' in data:
            match._id = data['_id']
        return match

    def validate(self) -> List[str]:
        """驗證資料是否有效"""
        errors = []
        
        if not self.tournament or len(self.tournament.strip()) < 2:
            errors.append("賽事名稱至少需要2個字符")
        
        if not self.season or len(self.season.strip()) < 2:
            errors.append("賽季資訊不能為空")
        
        if not self.team_a_id or not self.team_b_id:
            errors.append("必須指定參賽隊伍")
        
        if self.team_a_id == self.team_b_id:
            errors.append("參賽隊伍不能相同")
        
        if self.date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            if self.status == 'scheduled':
                errors.append("預定比賽時間不能早於今天")
        
        if self.team_a_score < 0 or self.team_b_score < 0:
            errors.append("比分不能為負數")
        
        if self.status not in ['scheduled', 'live', 'finished', 'cancelled']:
            errors.append("狀態必須是 scheduled, live, finished 或 cancelled")
        
        if self.match_format not in ['BO1', 'BO3', 'BO5']:
            errors.append("比賽格式必須是 BO1, BO3 或 BO5")
        
        if self.status == 'finished' and not self.result:
            errors.append("已完成的比賽必須有結果")
        
        if self.result and self.result not in ['win_a', 'win_b', 'draw']:
            errors.append("比賽結果必須是 win_a, win_b 或 draw")
        
        return errors

    def save(self, db) -> bool:
        """儲存到資料庫"""
        try:
            # 更新時間
            self.updated_at = datetime.now()
            
            # 驗證資料
            errors = self.validate()
            if errors:
                raise ValueError(f"資料驗證失敗: {', '.join(errors)}")
            
            collection = db.matches
            
            if self._id:
                # 更新現有記錄
                result = collection.update_one(
                    {'_id': self._id},
                    {'$set': self.to_dict()}
                )
                return result.modified_count > 0
            else:
                # 插入新記錄
                result = collection.insert_one(self.to_dict())
                self._id = result.inserted_id
                return True
                
        except Exception as e:
            print(f"儲存比賽資料時發生錯誤: {str(e)}")
            return False

    @classmethod
    def find_by_id(cls, db, match_id: str) -> Optional['Match']:
        """根據ID查找比賽"""
        try:
            collection = db.matches
            data = collection.find_one({'_id': ObjectId(match_id)})
            if data:
                return cls.from_dict(data)
            return None
        except Exception as e:
            print(f"查找比賽時發生錯誤: {str(e)}")
            return None

    @classmethod
    def find_all(cls, db, skip: int = 0, limit: int = 20, 
                 tournament: Optional[str] = None,
                 season: Optional[str] = None,
                 status: Optional[str] = None,
                 team_id: Optional[str] = None,
                 start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None) -> List['Match']:
        """查找所有比賽（支援分頁和篩選）"""
        try:
            collection = db.matches
            query = {}
            
            if tournament:
                query['tournament'] = {'$regex': tournament, '$options': 'i'}
            if season:
                query['season'] = season
            if status:
                query['status'] = status
            if team_id:
                query['$or'] = [
                    {'team_a_id': team_id},
                    {'team_b_id': team_id}
                ]
            
            # 日期範圍篩選
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query['$gte'] = start_date
                if end_date:
                    date_query['$lte'] = end_date
                query['date'] = date_query
            
            cursor = collection.find(query).sort('date', -1).skip(skip).limit(limit)
            matches = []
            
            for data in cursor:
                match = cls.from_dict(data)
                matches.append(match)
            
            return matches
            
        except Exception as e:
            print(f"查找比賽列表時發生錯誤: {str(e)}")
            return []

    @classmethod
    def find_upcoming(cls, db, limit: int = 10) -> List['Match']:
        """查找即將到來的比賽"""
        try:
            collection = db.matches
            query = {
                'date': {'$gte': datetime.now()},
                'status': 'scheduled'
            }
            cursor = collection.find(query).sort('date', 1).limit(limit)
            
            matches = []
            for data in cursor:
                match = cls.from_dict(data)
                matches.append(match)
            
            return matches
            
        except Exception as e:
            print(f"查找即將到來的比賽時發生錯誤: {str(e)}")
            return []

    @classmethod
    def find_recent(cls, db, limit: int = 10) -> List['Match']:
        """查找最近的比賽"""
        try:
            collection = db.matches
            query = {
                'date': {'$lte': datetime.now()},
                'status': 'finished'
            }
            cursor = collection.find(query).sort('date', -1).limit(limit)
            
            matches = []
            for data in cursor:
                match = cls.from_dict(data)
                matches.append(match)
            
            return matches
            
        except Exception as e:
            print(f"查找最近比賽時發生錯誤: {str(e)}")
            return []

    def delete(self, db) -> bool:
        """刪除比賽"""
        try:
            if not self._id:
                return False
            
            collection = db.matches
            result = collection.delete_one({'_id': self._id})
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"刪除比賽時發生錯誤: {str(e)}")
            return False

    def update_score(self, db, team_a_score: int, team_b_score: int) -> bool:
        """更新比分"""
        try:
            self.team_a_score = team_a_score
            self.team_b_score = team_b_score
            
            # 自動判斷勝負
            if self.status == 'finished':
                if team_a_score > team_b_score:
                    self.result = 'win_a'
                elif team_b_score > team_a_score:
                    self.result = 'win_b'
                else:
                    self.result = 'draw'
            
            return self.save(db)
            
        except Exception as e:
            print(f"更新比分時發生錯誤: {str(e)}")
            return False

    def update_status(self, db, status: str) -> bool:
        """更新比賽狀態"""
        try:
            self.status = status
            
            # 如果比賽結束，自動設定結果
            if status == 'finished' and not self.result:
                if self.team_a_score > self.team_b_score:
                    self.result = 'win_a'
                elif self.team_b_score > self.team_a_score:
                    self.result = 'win_b'
                else:
                    self.result = 'draw'
            
            return self.save(db)
            
        except Exception as e:
            print(f"更新比賽狀態時發生錯誤: {str(e)}")
            return False

    def add_game_detail(self, db, game_detail: Dict[str, Any]) -> bool:
        """新增單場比賽詳情"""
        try:
            self.game_details.append(game_detail)
            return self.save(db)
            
        except Exception as e:
            print(f"新增比賽詳情時發生錯誤: {str(e)}")
            return False

    def get_teams_info(self, db) -> Dict[str, Any]:
        """獲取參賽隊伍資訊"""
        try:
            from team import Team
            
            team_a = Team.find_by_id(db, self.team_a_id)
            team_b = Team.find_by_id(db, self.team_b_id)
            
            return {
                'team_a': team_a.to_json() if team_a else None,
                'team_b': team_b.to_json() if team_b else None
            }
            
        except Exception as e:
            print(f"獲取隊伍資訊時發生錯誤: {str(e)}")
            return {'team_a': None, 'team_b': None}

    def is_live(self) -> bool:
        """判斷比賽是否正在進行"""
        return self.status == 'live'

    def is_finished(self) -> bool:
        """判斷比賽是否已結束"""
        return self.status == 'finished'

    def is_upcoming(self) -> bool:
        """判斷比賽是否即將開始"""
        return self.status == 'scheduled' and self.date > datetime.now()

    def get_winner(self) -> Optional[str]:
        """獲取勝利隊伍ID"""
        if self.result == 'win_a':
            return self.team_a_id
        elif self.result == 'win_b':
            return self.team_b_id
        return None

    def to_json(self) -> Dict[str, Any]:
        """轉換為JSON格式（用於API回傳）"""
        data = self.to_dict()
        if '_id' in data:
            data['id'] = str(data['_id'])
            del data['_id']
        
        # 格式化時間
        if isinstance(data['date'], datetime):
            data['date'] = data['date'].isoformat()
        if isinstance(data['created_at'], datetime):
            data['created_at'] = data['created_at'].isoformat()
        if isinstance(data['updated_at'], datetime):
            data['updated_at'] = data['updated_at'].isoformat()
        
        return data
