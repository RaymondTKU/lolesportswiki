# 建立虛構隊伍與選手資料到資料庫
from models.team import Team
from models.player import Player
from config import get_database
from datetime import datetime

# 連接資料庫

db = get_database()
team_col = db['teams']
player_col = db['players']

# 1. 建立幾個隊伍
teams = [
    Team(
        name="T1 Tigers",
        logo="/images/team-a.png",
        region="韓國",
        founded_year=2013,
        description="韓國傳奇戰隊，世界冠軍多次得主。",
        social_media={"twitter": "https://twitter.com/t1tigers"}
    ),
    Team(
        name="JDG Dragons",
        logo="/images/team-c.png",
        region="中國",
        founded_year=2017,
        description="中國新興強權，LPL賽區代表。",
        social_media={"weibo": "https://weibo.com/jdgdragons"}
    ),
    Team(
        name="G2 Samurai",
        logo="/images/team-e.png",
        region="歐洲",
        founded_year=2015,
        description="歐洲霸主，風格大膽創新。",
        social_media={"instagram": "https://instagram.com/g2samurai"}
    )
]

# 插入隊伍並記錄ID
team_ids = []
for t in teams:
    result = team_col.insert_one(t.to_dict())
    team_ids.append(result.inserted_id)

# 2. 建立幾個選手
players = [
    Player(
        nickname="FakerX",
        real_name="李相赫",
        position="Mid",
        team_id=str(team_ids[0]),
        avatar="/images/player-1.jpg",
        age=28,
        nationality="韓國",
        stats={"KDA": 3.2, "勝率": "78%"},
        biography="傳奇中路，T1靈魂人物。"
    ),
    Player(
        nickname="RulerZ",
        real_name="朴載赫",
        position="ADC",
        team_id=str(team_ids[1]),
        avatar="/images/player-2.jpg",
        age=25,
        nationality="韓國",
        stats={"KDA": 2.8, "勝率": "74%"},
        biography="JDG主力射手，團隊核心。"
    ),
    Player(
        nickname="CapsY",
        real_name="Rasmus Winther",
        position="Mid",
        team_id=str(team_ids[2]),
        avatar="/images/player-3.jpg",
        age=24,
        nationality="丹麥",
        stats={"KDA": 3.1, "勝率": "72%"},
        biography="G2中路，歐洲最強選手之一。"
    )
]

for p in players:
    player_col.insert_one(p.to_dict())

print("已建立虛構隊伍與選手資料！")
