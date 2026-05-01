from flask import Blueprint, request, jsonify, session
from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    
    if user.is_banned:
        return jsonify({'success': False, 'message': '该用户已被禁用'}), 403
    
    if not user.check_password(password):
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    
    session['user_id'] = user.id
    session['username'] = user.username
    session['is_admin'] = user.is_admin
    
    return jsonify({
        'success': True,
        'message': '登录成功',
        'data': {
            'user': user.to_dict()
        }
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': '已退出登录'})

@auth_bp.route('/current-user', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    return jsonify({
        'success': True,
        'data': {
            'user': user.to_dict()
        }
    })

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    data = request.get_json()
    old_password = data.get('oldPassword', '')
    new_password = data.get('newPassword', '')
    
    if not old_password or not new_password:
        return jsonify({'success': False, 'message': '旧密码和新密码不能为空'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    if not user.check_password(old_password):
        return jsonify({'success': False, 'message': '旧密码错误'}), 400
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '密码修改成功'})
