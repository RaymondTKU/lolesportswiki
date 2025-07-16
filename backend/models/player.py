from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from bson import ObjectId
from pymongo import MongoClient
import os

@dataclass
class Player:
    """選手資料模型"""
    nickname: str
    real_name: str
    position: str
    team_id: Optional[str] = None
    avatar: str = ""
    age: Optional[int] = None
    nationality: str = ""
    stats: Dict[str, Any] = field(default_factory=dict)
    social_media: Dict[str, str] = field(default_factory=dict)
    biography: str = ""
    achievements: List[str] = field(default_factory=list)
    status: str = "active"  # active, inactive, retired
    join_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    _id: Optional[ObjectId] = None

    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
        if isinstance(self.join_date, str):
            self.join_date = datetime.fromisoformat(self.join_date)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式用於MongoDB存儲"""
        data = {
            'nickname': self.nickname,
            'real_name': self.real_name,
            'position': self.position,
            'team_id': self.team_id,
            'avatar': self.avatar,
            'age': self.age,
            'nationality': self.nationality,
            'stats': self.stats,
            'social_media': self.social_media,
            'biography': self.biography,
            'achievements': self.achievements,
            'status': self.status,
            'join_date': self.join_date,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        if self._id:
            data['_id'] = self._id
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """從字典創建Player實例"""
        player = cls(
            nickname=data['nickname'],
            real_name=data['real_name'],
            position=data['position'],
            team_id=data.get('team_id'),
            avatar=data.get('avatar', ''),
            age=data.get('age'),
            nationality=data.get('nationality', ''),
            stats=data.get('stats', {}),
            social_media=data.get('social_media', {}),
            biography=data.get('biography', ''),
            achievements=data.get('achievements', []),
            status=data.get('status', 'active'),
            join_date=data.get('join_date'),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now())
        )
        if '_id' in data:
            player._id = data['_id']
        return player

    def validate(self) -> List[str]:
        """驗證資料是否有效"""
        errors = []
        
        if not self.nickname or len(self.nickname.strip()) < 2:
            errors.append("遊戲暱稱至少需要2個字符")
        
        if not self.real_name or len(self.real_name.strip()) < 2:
            errors.append("真實姓名至少需要2個字符")
        
        valid_positions = ['top', 'jungle', 'mid', 'adc', 'support', 'coach', 'substitute']
        if not self.position or self.position.lower() not in valid_positions:
            errors.append(f"位置必須是以下之一: {', '.join(valid_positions)}")
        
        if self.age is not None and (self.age < 16 or self.age > 40):
            errors.append("年齡必須在16-40歲之間")
        
        if self.avatar and not self.avatar.startswith(('http://', 'https://', '/')):
            errors.append("頭像URL格式不正確")
        
        if self.status not in ['active', 'inactive', 'retired']:
            errors.append("狀態必須是 active, inactive 或 retired")
        
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
            
            collection = db.players
            
            if self._id:
                # 更新現有記錄
                result = collection.update_one(
                    {'_id': self._id},
                    {'$set': self.to_dict()}
                )
                return result.modified_count > 0
            else:
                # 檢查是否已存在同名選手
                existing = collection.find_one({'nickname': self.nickname})
                if existing:
                    raise ValueError(f"選手暱稱 '{self.nickname}' 已存在")
                
                # 插入新記錄
                result = collection.insert_one(self.to_dict())
                self._id = result.inserted_id
                return True
                
        except Exception as e:
            print(f"儲存選手資料時發生錯誤: {str(e)}")
            return False

    @classmethod
    def find_by_id(cls, db, player_id: str) -> Optional['Player']:
        """根據ID查找選手"""
        try:
            collection = db.players
            data = collection.find_one({'_id': ObjectId(player_id)})
            if data:
                return cls.from_dict(data)
            return None
        except Exception as e:
            print(f"查找選手時發生錯誤: {str(e)}")
            return None

    @classmethod
    def find_all(cls, db, skip: int = 0, limit: int = 20, 
                 team_id: Optional[str] = None,
                 position: Optional[str] = None,
                 status: Optional[str] = None) -> List['Player']:
        """查找所有選手（支援分頁和篩選）"""
        try:
            collection = db.players
            query = {}
            
            if team_id:
                query['team_id'] = team_id
            if position:
                query['position'] = position
            if status:
                query['status'] = status
            
            cursor = collection.find(query).skip(skip).limit(limit)
            players = []
            
            for data in cursor:
                player = cls.from_dict(data)
                players.append(player)
            
            return players
            
        except Exception as e:
            print(f"查找選手列表時發生錯誤: {str(e)}")
            return []

    @classmethod
    def search_by_nickname(cls, db, nickname: str) -> List['Player']:
        """根據暱稱搜索選手"""
        try:
            collection = db.players
            query = {'nickname': {'$regex': nickname, '$options': 'i'}}
            cursor = collection.find(query)
            
            players = []
            for data in cursor:
                player = cls.from_dict(data)
                players.append(player)
            
            return players
            
        except Exception as e:
            print(f"搜索選手時發生錯誤: {str(e)}")
            return []

    @classmethod
    def find_by_team(cls, db, team_id: str) -> List['Player']:
        """根據隊伍ID查找選手"""
        try:
            collection = db.players
            cursor = collection.find({'team_id': team_id})
            
            players = []
            for data in cursor:
                player = cls.from_dict(data)
                players.append(player)
            
            return players
            
        except Exception as e:
            print(f"查找隊伍選手時發生錯誤: {str(e)}")
            return []

    def delete(self, db) -> bool:
        """刪除選手"""
        try:
            if not self._id:
                return False
            
            collection = db.players
            result = collection.delete_one({'_id': self._id})
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"刪除選手時發生錯誤: {str(e)}")
            return False

    def update_team(self, db, team_id: Optional[str]) -> bool:
        """更新隊伍"""
        try:
            old_team_id = self.team_id
            self.team_id = team_id
            
            if self.save(db):
                # 如果有舊隊伍，從舊隊伍中移除
                if old_team_id:
                    from team import Team
                    old_team = Team.find_by_id(db, old_team_id)
                    if old_team:
                        old_team.remove_member(db, str(self._id))
                
                # 如果有新隊伍，加入新隊伍
                if team_id:
                    from team import Team
                    new_team = Team.find_by_id(db, team_id)
                    if new_team:
                        new_team.add_member(db, str(self._id))
                
                return True
            
            return False
            
        except Exception as e:
            print(f"更新選手隊伍時發生錯誤: {str(e)}")
            return False

    def update_statistics(self, db, stats: Dict[str, Any]) -> bool:
        """更新統計數據"""
        try:
            self.stats.update(stats)
            return self.save(db)
            
        except Exception as e:
            print(f"更新統計數據時發生錯誤: {str(e)}")
            return False

    def add_achievement(self, db, achievement: str) -> bool:
        """新增成就"""
        try:
            if achievement not in self.achievements:
                self.achievements.append(achievement)
                return self.save(db)
            return True
            
        except Exception as e:
            print(f"新增成就時發生錯誤: {str(e)}")
            return False

    def get_team_info(self, db) -> Optional[Dict[str, Any]]:
        """獲取隊伍資訊"""
        try:
            if not self.team_id:
                return None
            
            from team import Team
            team = Team.find_by_id(db, self.team_id)
            if team:
                return team.to_json()
            return None
            
        except Exception as e:
            print(f"獲取隊伍資訊時發生錯誤: {str(e)}")
            return None

    def to_json(self) -> Dict[str, Any]:
        """轉換為JSON格式（用於API回傳）"""
        data = self.to_dict()
        if '_id' in data:
            data['id'] = str(data['_id'])
            del data['_id']
        
        # 格式化時間
        if isinstance(data['created_at'], datetime):
            data['created_at'] = data['created_at'].isoformat()
        if isinstance(data['updated_at'], datetime):
            data['updated_at'] = data['updated_at'].isoformat()
        if data['join_date'] and isinstance(data['join_date'], datetime):
            data['join_date'] = data['join_date'].isoformat()
        
        return data
