"""
英雄聯盟電競資訊網 API
主要執行文件
"""

import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.config import config, get_database
from backend.routes.auth import auth_bp
from backend.routes.teams import team_bp  
from backend.routes.players import player_bp
from backend.routes.matches import match_bp

def create_app(config_name=None):
    """應用程式工廠"""
    app = Flask(__name__)
    
    # 設定配置
    config_name = config_name or os.environ.get('FLASK_CONFIG', 'default')
    app.config.from_object(config[config_name])
    
    # 設定 CORS（允許所有來源）
    CORS(app)
    
    # 初始化 JWT
    jwt = JWTManager(app)
    
    # 測試資料庫連接
    try:
        db = get_database()
        print(f"成功連接到資料庫: {db.name}")
    except Exception as e:
        print(f"資料庫連接失敗: {str(e)}")
        raise
    
    # 註冊藍圖
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(team_bp, url_prefix='/api')
    app.register_blueprint(player_bp, url_prefix='/api')
    app.register_blueprint(match_bp, url_prefix='/api')
    
    # 根路由
    @app.route('/')
    def index():
        return jsonify({
            'message': '英雄聯盟電競資訊網 API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'auth': '/api/auth',
                'teams': '/api/teams',
                'players': '/api/players',
                'matches': '/api/matches'
            }
        })
    
    # 健康檢查
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})
    
    # API 資訊
    @app.route('/api')
    def api_info():
        return jsonify({
            'api_version': '1.0.0',
            'endpoints': {
                'auth': {
                    'register': 'POST /api/auth/register',
                    'login': 'POST /api/auth/login',
                    'me': 'GET /api/auth/me'
                },
                'teams': {
                    'list': 'GET /api/teams',
                    'create': 'POST /api/teams',
                    'detail': 'GET /api/teams/<id>',
                    'update': 'PUT /api/teams/<id>',
                    'delete': 'DELETE /api/teams/<id>'
                },
                'players': {
                    'list': 'GET /api/players',
                    'create': 'POST /api/players',
                    'detail': 'GET /api/players/<id>',
                    'update': 'PUT /api/players/<id>',
                    'delete': 'DELETE /api/players/<id>'
                },
                'matches': {
                    'list': 'GET /api/matches',
                    'create': 'POST /api/matches',
                    'detail': 'GET /api/matches/<id>',
                    'update': 'PUT /api/matches/<id>',
                    'delete': 'DELETE /api/matches/<id>',
                    'upcoming': 'GET /api/matches/upcoming',
                    'recent': 'GET /api/matches/recent',
                    'live': 'GET /api/matches/live'
                }
            }
        })
    
    # 錯誤處理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': '找不到請求的資源'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'message': '伺服器內部錯誤'
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': '請求格式不正確'
        }), 400
    
    return app

if __name__ == '__main__':
    # 創建應用程式實例
    app = create_app()
    
    # 啟動開發伺服器
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True
    )
