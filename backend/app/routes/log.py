from flask import Blueprint, request, jsonify, session
from app import db
from app.models.operation_log import OperationLog
from app.models.asset import Asset

log_bp = Blueprint('log', __name__)

def require_login():
    if not session.get('user_id'):
        return jsonify({'code': 401, 'message': '请先登录'}), 401
    return None

@log_bp.route('/logs', methods=['GET'])
def get_logs():
    if require_login():
        return require_login()
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    start_date = request.args.get('startDate', '')
    end_date = request.args.get('endDate', '')
    operator = request.args.get('operator', '')
    asset_code = request.args.get('assetCode', '')

    query = OperationLog.query

    if start_date:
        query = query.filter(OperationLog.created_at >= start_date)
    if end_date:
        query = query.filter(OperationLog.created_at <= end_date)
    if operator:
        query = query.filter(OperationLog.operator.like(f'%{operator}%'))
    if asset_code:
        query = query.join(Asset).filter(Asset.asset_code.like(f'%{asset_code}%'))

    query = query.order_by(OperationLog.created_at.desc())

    total = query.count()
    logs = query.offset((page - 1) * page_size).limit(page_size).all()

    return jsonify({
        'code': 200,
        'data': {
            'items': [log.to_dict() for log in logs],
            'total': total,
            'page': page,
            'pageSize': page_size
        }
    })

@log_bp.route('/logs/<asset_id>', methods=['GET'])
def get_asset_logs(asset_id):
    if require_login():
        return require_login()
    
    logs = OperationLog.query.filter(
        OperationLog.asset_id == asset_id
    ).order_by(OperationLog.created_at.desc()).all()

    return jsonify({
        'code': 200,
        'data': [log.to_dict() for log in logs]
    })
