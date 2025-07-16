from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from models.database import db
from routes.auth import auth_bp
from routes.teams import team_bp
from routes.players import player_bp
from routes.matches import match_bp
from routes.comments import comments_bp
from routes.favorites import favorites_bp
from routes.admin import admin_bp
from routes.upload import upload_bp
import os

def create_app(config_name=None):
    """應用程式工廠"""
    app = Flask(__name__)
    
    # 設定配置
    config_name = config_name or os.environ.get('FLASK_CONFIG', 'default')
    app.config.from_object(config[config_name])
    
    # 設定 CORS
    CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:5500'])
    
    # 初始化 JWT
    jwt = JWTManager(app)
    
    # 初始化資料庫
    if not db.connect(app.config['MONGODB_URI']):
        raise Exception("無法連接到資料庫")
    
    # 註冊藍圖
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(team_bp, url_prefix='/api')
    app.register_blueprint(player_bp, url_prefix='/api')
    app.register_blueprint(match_bp, url_prefix='/api')
    app.register_blueprint(comments_bp, url_prefix='/api')
    app.register_blueprint(favorites_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    
    # 靜態檔案服務
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory('uploads', filename)
    
    # 根路由
    @app.route('/')
    def index():
        return jsonify({
            'message': '英雄聯盟電競資訊網 API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'teams': '/api/teams',
                'players': '/api/players',
                'matches': '/api/matches',
                'comments': '/api/comments',
                'favorites': '/api/favorites',
                'admin': '/api/admin',
                'upload': '/api/upload'
            }
        })
    
    # 健康檢查
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})
    
    # 錯誤處理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': '找不到請求的資源'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'message': '伺服器內部錯誤'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
