# 將8支隊伍的LOGO加入資料庫
from models.team import Team
from config import get_database
from datetime import datetime

# 連接資料庫
db = get_database()
team_col = db['teams']

# 定義8支隊伍的資料
teams_data = [
    {
        "name": "CFO",
        "logo": "/images/CFOlogo.webp",
        "region": "台灣",
        "founded_year": 2020,
        "description": "台灣電競戰隊CFO",
        "social_media": {"twitter": "https://twitter.com/CFO_esports"}
    },
    {
        "name": "CHF",
        "logo": "/images/CHFlogo.webp", 
        "region": "中國",
        "founded_year": 2019,
        "description": "中國電競戰隊CHF",
        "social_media": {"weibo": "https://weibo.com/CHF_esports"}
    },
    {
        "name": "DFM",
        "logo": "/images/DFMlogo.webp",
        "region": "日本", 
        "founded_year": 2018,
        "description": "日本電競戰隊DetonationFocusMe",
        "social_media": {"twitter": "https://twitter.com/DFM_gg"}
    },
    {
        "name": "GAM",
        "logo": "/images/GAMlogo.webp",
        "region": "越南",
        "founded_year": 2017,
        "description": "越南電競戰隊GAM Esports",
        "social_media": {"facebook": "https://facebook.com/GAMEsports"}
    },
    {
        "name": "MVKE",
        "logo": "/images/MVKElogo.webp",
        "region": "韓國",
        "founded_year": 2021,
        "description": "韓國新興電競戰隊MVKE",
        "social_media": {"twitter": "https://twitter.com/MVKE_esports"}
    },
    {
        "name": "PSG",
        "logo": "/images/PSGlogo.webp",
        "region": "台灣",
        "founded_year": 2020,
        "description": "PSG電競戰隊台灣分部",
        "social_media": {"instagram": "https://instagram.com/PSG_esports"}
    },
    {
        "name": "SHG",
        "logo": "/images/SHGlogo.webp",
        "region": "中國",
        "founded_year": 2019,
        "description": "中國電競戰隊SHG",
        "social_media": {"weibo": "https://weibo.com/SHG_gaming"}
    },
    {
        "name": "TSW",
        "logo": "/images/TSWlogo.webp",
        "region": "泰國",
        "founded_year": 2020,
        "description": "泰國電競戰隊Team Secret Wild",
        "social_media": {"twitter": "https://twitter.com/TSW_esports"}
    }
]

print("開始插入隊伍資料...")

# 先清除現有的隊伍資料（可選）
# team_col.delete_many({})

# 插入新的隊伍資料
inserted_count = 0
for team_data in teams_data:
    # 檢查是否已存在同名隊伍
    existing_team = team_col.find_one({"name": team_data["name"]})
    if existing_team:
        print(f"隊伍 {team_data['name']} 已存在，跳過...")
        continue
        
    team = Team(
        name=team_data["name"],
        logo=team_data["logo"],
        region=team_data["region"],
        founded_year=team_data["founded_year"],
        description=team_data["description"],
        social_media=team_data["social_media"],
        members=[],  # 暫時沒有選手
        statistics={},  # 暫時沒有統計資料
        status="active"
    )
    
    result = team_col.insert_one(team.to_dict())
    inserted_count += 1
    print(f"已插入隊伍: {team_data['name']} (ID: {result.inserted_id})")

print(f"\n完成！總共插入了 {inserted_count} 支隊伍")

# 顯示所有隊伍
print("\n所有隊伍列表:")
all_teams = team_col.find({})
for team in all_teams:
    print(f"- {team['name']} ({team['region']}) - {team['logo']}")
