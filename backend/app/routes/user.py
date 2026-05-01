from flask import Blueprint, request, jsonify, session
from app import db
from app.models.user import User

user_bp = Blueprint('user', __name__)

def require_admin():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '需要管理员权限'}), 403
    return None

@user_bp.route('/users', methods=['GET'])
def get_users():
    if require_admin():
        return require_admin()
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    
    query = User.query.order_by(User.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    return jsonify({
        'success': True,
        'data': {
            'items': [u.to_dict() for u in pagination.items],
            'page': page,
            'pageSize': page_size,
            'total': pagination.total
        }
    })

@user_bp.route('/users', methods=['POST'])
def create_user():
    if require_admin():
        return require_admin()
    
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'success': False, 'message': '用户名不能为空'}), 400
    
    import re
    if not re.match(r'^[a-zA-Z]+$', username):
        return jsonify({'success': False, 'message': '用户名只能包含英文字母'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    
    user = User(username=username)
    user.set_password(username)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '用户创建成功，初始密码与用户名相同',
        'data': {
            'user': user.to_dict()
        }
    })

@user_bp.route('/users/<int:user_id>/ban', methods=['POST'])
def ban_user(user_id):
    if require_admin():
        return require_admin()
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    if user.is_admin:
        return jsonify({'success': False, 'message': '不能禁用管理员账户'}), 400
    
    user.is_banned = True
    db.session.commit()
    
    return jsonify({'success': True, 'message': '用户已禁用'})

@user_bp.route('/users/<int:user_id>/unban', methods=['POST'])
def unban_user(user_id):
    if require_admin():
        return require_admin()
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    user.is_banned = False
    db.session.commit()
    
    return jsonify({'success': True, 'message': '用户已启用'})

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if require_admin():
        return require_admin()
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    if user.is_admin:
        return jsonify({'success': False, 'message': '不能删除管理员账户'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '用户已删除'})
