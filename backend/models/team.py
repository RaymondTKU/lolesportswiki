from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from bson import ObjectId
from pymongo import MongoClient
import os

@dataclass
class Team:
    """隊伍資料模型"""
    name: str
    logo: str
    region: str
    founded_year: int
    members: List[str] = field(default_factory=list)  # player_ids
    statistics: Dict[str, Any] = field(default_factory=dict)
    social_media: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    status: str = "active"  # active, inactive, disbanded
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    _id: Optional[ObjectId] = None

    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式用於MongoDB存儲"""
        data = {
            'name': self.name,
            'logo': self.logo,
            'region': self.region,
            'founded_year': self.founded_year,
            'members': self.members,
            'statistics': self.statistics,
            'social_media': self.social_media,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        if self._id:
            data['_id'] = self._id
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Team':
        """從字典創建Team實例"""
        team = cls(
            name=data['name'],
            logo=data['logo'],
            region=data['region'],
            founded_year=data['founded_year'],
            members=data.get('members', []),
            statistics=data.get('statistics', {}),
            social_media=data.get('social_media', {}),
            description=data.get('description', ''),
            status=data.get('status', 'active'),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now())
        )
        if '_id' in data:
            team._id = data['_id']
        return team

    def validate(self) -> List[str]:
        """驗證資料是否有效"""
        errors = []
        
        if not self.name or len(self.name.strip()) < 2:
            errors.append("隊伍名稱至少需要2個字符")
        
        if not self.region or len(self.region.strip()) < 2:
            errors.append("地區資訊不能為空")
        
        if not self.logo or not self.logo.startswith(('http://', 'https://', '/')):
            errors.append("Logo URL格式不正確")
        
        if self.founded_year < 2009 or self.founded_year > datetime.now().year:
            errors.append("成立年份不合理")
        
        if self.status not in ['active', 'inactive', 'disbanded']:
            errors.append("狀態必須是 active, inactive 或 disbanded")
        
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
            
            collection = db.teams
            
            if self._id:
                # 更新現有記錄
                result = collection.update_one(
                    {'_id': self._id},
                    {'$set': self.to_dict()}
                )
                return result.modified_count > 0
            else:
                # 檢查是否已存在同名隊伍
                existing = collection.find_one({'name': self.name})
                if existing:
                    raise ValueError(f"隊伍名稱 '{self.name}' 已存在")
                
                # 插入新記錄
                result = collection.insert_one(self.to_dict())
                self._id = result.inserted_id
                return True
                
        except Exception as e:
            print(f"儲存隊伍資料時發生錯誤: {str(e)}")
            return False

    @classmethod
    def find_by_id(cls, db, team_id: str) -> Optional['Team']:
        """根據ID查找隊伍"""
        try:
            collection = db.teams
            data = collection.find_one({'_id': ObjectId(team_id)})
            if data:
                return cls.from_dict(data)
            return None
        except Exception as e:
            print(f"查找隊伍時發生錯誤: {str(e)}")
            return None

    @classmethod
    def find_all(cls, db, skip: int = 0, limit: int = 20, 
                 region: Optional[str] = None, 
                 status: Optional[str] = None) -> List['Team']:
        """查找所有隊伍（支援分頁和篩選）"""
        try:
            collection = db.teams
            query = {}
            
            if region:
                query['region'] = region
            if status:
                query['status'] = status
            
            cursor = collection.find(query).skip(skip).limit(limit)
            teams = []
            
            for data in cursor:
                team = cls.from_dict(data)
                teams.append(team)
            
            return teams
            
        except Exception as e:
            print(f"查找隊伍列表時發生錯誤: {str(e)}")
            return []

    @classmethod
    def search_by_name(cls, db, name: str) -> List['Team']:
        """根據名稱搜索隊伍"""
        try:
            collection = db.teams
            query = {'name': {'$regex': name, '$options': 'i'}}
            cursor = collection.find(query)
            
            teams = []
            for data in cursor:
                team = cls.from_dict(data)
                teams.append(team)
            
            return teams
            
        except Exception as e:
            print(f"搜索隊伍時發生錯誤: {str(e)}")
            return []

    def delete(self, db) -> bool:
        """刪除隊伍"""
        try:
            if not self._id:
                return False
            
            collection = db.teams
            result = collection.delete_one({'_id': self._id})
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"刪除隊伍時發生錯誤: {str(e)}")
            return False

    def add_member(self, db, player_id: str) -> bool:
        """新增隊員"""
        try:
            if player_id not in self.members:
                self.members.append(player_id)
                return self.save(db)
            return True
            
        except Exception as e:
            print(f"新增隊員時發生錯誤: {str(e)}")
            return False

    def remove_member(self, db, player_id: str) -> bool:
        """移除隊員"""
        try:
            if player_id in self.members:
                self.members.remove(player_id)
                return self.save(db)
            return True
            
        except Exception as e:
            print(f"移除隊員時發生錯誤: {str(e)}")
            return False

    def update_statistics(self, db, stats: Dict[str, Any]) -> bool:
        """更新統計數據"""
        try:
            self.statistics.update(stats)
            return self.save(db)
            
        except Exception as e:
            print(f"更新統計數據時發生錯誤: {str(e)}")
            return False

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
        
        return data
