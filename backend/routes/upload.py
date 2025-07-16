from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from PIL import Image
import os
import uuid
import logging

upload_bp = Blueprint('upload', __name__)

# 允許的圖片格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 圖片大小限制 (bytes)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """檢查檔案格式是否允許"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image_path, max_size=(800, 600)):
    """調整圖片大小"""
    try:
        with Image.open(image_path) as img:
            # 轉換為RGB格式（如果需要）
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # 計算新的大小
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 儲存調整後的圖片
            img.save(image_path, optimize=True, quality=85)
            return True
    except Exception as e:
        logging.error(f"圖片調整失敗: {str(e)}")
        return False

@upload_bp.route('/image', methods=['POST'])
@jwt_required()
def upload_image():
    """上傳圖片"""
    try:
        # 檢查是否有檔案
        if 'file' not in request.files:
            return jsonify({'message': '沒有選擇檔案'}), 400
        
        file = request.files['file']
        
        # 檢查檔案名稱
        if file.filename == '':
            return jsonify({'message': '沒有選擇檔案'}), 400
        
        # 檢查檔案格式
        if not allowed_file(file.filename):
            return jsonify({'message': '不支援的檔案格式'}), 400
        
        # 檢查檔案大小
        if file.content_length and file.content_length > MAX_FILE_SIZE:
            return jsonify({'message': '檔案太大，請選擇小於5MB的檔案'}), 400
        
        # 產生唯一檔名
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # 建立上傳目錄
        upload_folder = os.path.join('uploads', 'images')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # 儲存檔案
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # 調整圖片大小
        if not resize_image(file_path):
            os.remove(file_path)
            return jsonify({'message': '圖片處理失敗'}), 500
        
        # 返回檔案URL
        file_url = f"/uploads/images/{unique_filename}"
        
        return jsonify({
            'message': '圖片上傳成功',
            'file_url': file_url,
            'filename': unique_filename
        })
        
    except Exception as e:
        logging.error(f"圖片上傳失敗: {str(e)}")
        return jsonify({'message': '圖片上傳失敗'}), 500

@upload_bp.route('/team-logo', methods=['POST'])
@jwt_required()
def upload_team_logo():
    """上傳隊伍Logo"""
    try:
        # 檢查是否有檔案
        if 'file' not in request.files:
            return jsonify({'message': '沒有選擇檔案'}), 400
        
        file = request.files['file']
        
        # 檢查檔案名稱
        if file.filename == '':
            return jsonify({'message': '沒有選擇檔案'}), 400
        
        # 檢查檔案格式
        if not allowed_file(file.filename):
            return jsonify({'message': '不支援的檔案格式'}), 400
        
        # 產生唯一檔名
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"team_logo_{uuid.uuid4()}.{file_extension}"
        
        # 建立上傳目錄
        upload_folder = os.path.join('uploads', 'team_logos')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # 儲存檔案
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # 調整圖片大小為正方形Logo
        if not resize_image(file_path, max_size=(200, 200)):
            os.remove(file_path)
            return jsonify({'message': '圖片處理失敗'}), 500
        
        # 返回檔案URL
        file_url = f"/uploads/team_logos/{unique_filename}"
        
        return jsonify({
            'message': '隊伍Logo上傳成功',
            'file_url': file_url,
            'filename': unique_filename
        })
        
    except Exception as e:
        logging.error(f"隊伍Logo上傳失敗: {str(e)}")
        return jsonify({'message': '隊伍Logo上傳失敗'}), 500

@upload_bp.route('/player-avatar', methods=['POST'])
@jwt_required()
def upload_player_avatar():
    """上傳選手頭像"""
    try:
        # 檢查是否有檔案
        if 'file' not in request.files:
            return jsonify({'message': '沒有選擇檔案'}), 400
        
        file = request.files['file']
        
        # 檢查檔案名稱
        if file.filename == '':
            return jsonify({'message': '沒有選擇檔案'}), 400
        
        # 檢查檔案格式
        if not allowed_file(file.filename):
            return jsonify({'message': '不支援的檔案格式'}), 400
        
        # 產生唯一檔名
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"player_avatar_{uuid.uuid4()}.{file_extension}"
        
        # 建立上傳目錄
        upload_folder = os.path.join('uploads', 'player_avatars')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # 儲存檔案
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # 調整圖片大小為正方形頭像
        if not resize_image(file_path, max_size=(300, 300)):
            os.remove(file_path)
            return jsonify({'message': '圖片處理失敗'}), 500
        
        # 返回檔案URL
        file_url = f"/uploads/player_avatars/{unique_filename}"
        
        return jsonify({
            'message': '選手頭像上傳成功',
            'file_url': file_url,
            'filename': unique_filename
        })
        
    except Exception as e:
        logging.error(f"選手頭像上傳失敗: {str(e)}")
        return jsonify({'message': '選手頭像上傳失敗'}), 500

@upload_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_image():
    """刪除圖片"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'message': '缺少檔案名稱'}), 400
        
        # 安全檢查：確保檔名安全
        filename = secure_filename(filename)
        
        # 尋找檔案
        possible_paths = [
            os.path.join('uploads', 'images', filename),
            os.path.join('uploads', 'team_logos', filename),
            os.path.join('uploads', 'player_avatars', filename)
        ]
        
        file_deleted = False
        for file_path in possible_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
                file_deleted = True
                break
        
        if file_deleted:
            return jsonify({'message': '圖片刪除成功'})
        else:
            return jsonify({'message': '找不到指定的圖片'}), 404
        
    except Exception as e:
        logging.error(f"圖片刪除失敗: {str(e)}")
        return jsonify({'message': '圖片刪除失敗'}), 500
