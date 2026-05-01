from flask import Blueprint, request, jsonify, session, send_file
from app import db
from app.models.asset import Asset
from app.models.mac_address import MacAddress
from app.services.asset_service import AssetService
import pandas as pd
from io import BytesIO
import uuid

asset_bp = Blueprint('asset', __name__)

def require_login():
    if not session.get('user_id'):
        return jsonify({'code': 401, 'message': '请先登录'}), 401
    return None

def get_current_user():
    return session.get('username', 'system')

@asset_bp.route('/assets', methods=['GET'])
def get_assets():
    if require_login():
        return require_login()

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    asset_code = request.args.get('assetCode', '')
    machine_model = request.args.get('machineModel', '')
    machine_type = request.args.get('machineType', '')
    status = request.args.get('status', '')
    user_name = request.args.get('userName', '')
    device_id = request.args.get('deviceId', '')
    mac = request.args.get('mac', '')
    ip = request.args.get('ip', '')

    query = Asset.query

    if asset_code:
        query = query.filter(Asset.asset_code.like(f'%{asset_code}%'))
    if machine_model:
        query = query.filter(Asset.machine_model.like(f'%{machine_model}%'))
    if machine_type:
        query = query.filter(Asset.machine_type == machine_type)
    if status:
        query = query.filter(Asset.status == status)
    if device_id:
        query = query.filter(Asset.device_id.like(f'%{device_id}%'))

    if mac:
        query = query.join(MacAddress).filter(MacAddress.mac.like(f'%{mac.upper()}%'))
    if ip:
        query = query.join(MacAddress).filter(MacAddress.ip.like(f'%{ip}%'))

    if user_name:
        from app.models.usage_record import UsageRecord
        query = query.join(UsageRecord).filter(UsageRecord.user_name.like(f'%{user_name}%'))

    query = query.order_by(Asset.created_at.desc())

    total = query.count()
    assets = query.offset((page - 1) * page_size).limit(page_size).all()

    return jsonify({
        'code': 200,
        'data': {
            'items': [asset.to_simple_dict() for asset in assets],
            'total': total,
            'page': page,
            'pageSize': page_size
        }
    })

@asset_bp.route('/assets/<asset_id>', methods=['GET'])
def get_asset(asset_id):
    if require_login():
        return require_login()

    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({'code': 404, 'message': 'Asset not found'}), 404

    return jsonify({
        'code': 200,
        'data': asset.to_dict()
    })

@asset_bp.route('/assets', methods=['POST'])
def create_asset():
    if require_login():
        return require_login()

    data = request.get_json()
    data['operator'] = get_current_user()

    if not data.get('machine_model'):
        return jsonify({'code': 400, 'message': 'machine_model is required'}), 400
    if not data.get('machine_type'):
        return jsonify({'code': 400, 'message': 'machine_type is required'}), 400

    asset = AssetService.create_asset(data)

    return jsonify({
        'code': 200,
        'data': asset.to_dict()
    })

@asset_bp.route('/assets/<asset_id>', methods=['PUT'])
def update_asset(asset_id):
    if require_login():
        return require_login()

    data = request.get_json()
    data['operator'] = get_current_user()

    asset = AssetService.update_asset(asset_id, data)
    if not asset:
        return jsonify({'code': 404, 'message': 'Asset not found'}), 404

    return jsonify({
        'code': 200,
        'data': asset.to_dict()
    })

@asset_bp.route('/assets/<asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    if require_login():
        return require_login()

    operator = request.args.get('operator', get_current_user())

    result, error = AssetService.delete_asset(asset_id, operator)
    if error:
        return jsonify({'code': 404, 'message': error}), 404

    return jsonify({
        'code': 200,
        'message': 'Asset deleted successfully'
    })

@asset_bp.route('/assets/<asset_id>/claim', methods=['POST'])
def claim_asset(asset_id):
    if require_login():
        return require_login()

    data = request.get_json()
    data['operator'] = get_current_user()

    if not data.get('user_name'):
        return jsonify({'code': 400, 'message': 'user_name is required'}), 400

    asset, error = AssetService.claim_asset(asset_id, data)
    if error:
        return jsonify({'code': 409, 'message': error}), 409

    return jsonify({
        'code': 200,
        'data': asset.to_dict()
    })

@asset_bp.route('/assets/<asset_id>/retire', methods=['POST'])
def retire_asset(asset_id):
    if require_login():
        return require_login()

    data = request.get_json()
    data['operator'] = get_current_user()

    asset, error = AssetService.retire_asset(asset_id, data)
    if error:
        return jsonify({'code': 404, 'message': error}), 404

    return jsonify({
        'code': 200,
        'data': asset.to_dict()
    })

@asset_bp.route('/assets/<asset_id>/change-user', methods=['POST'])
def change_asset_user(asset_id):
    if require_login():
        return require_login()

    data = request.get_json()
    data['operator'] = get_current_user()

    if not data.get('user_name'):
        return jsonify({'code': 400, 'message': 'user_name is required'}), 400

    asset, error = AssetService.change_asset_user(asset_id, data)
    if error:
        return jsonify({'code': 404, 'message': error}), 404

    return jsonify({
        'code': 200,
        'data': asset.to_dict()
    })

@asset_bp.route('/assets/<asset_id>/return', methods=['POST'])
def return_to_storage(asset_id):
    if require_login():
        return require_login()

    data = request.get_json()
    data['operator'] = get_current_user()

    asset, error = AssetService.return_to_storage(asset_id, data)
    if error:
        return jsonify({'code': 404, 'message': error}), 404

    return jsonify({
        'code': 200,
        'data': asset.to_dict()
    })

@asset_bp.route('/assets/pending', methods=['GET'])
def get_pending_assets():
    if require_login():
        return require_login()

    assets = AssetService.get_pending_assets()

    return jsonify({
        'code': 200,
        'data': [asset.to_simple_dict() for asset in assets]
    })

@asset_bp.route('/assets/<asset_id>/mac', methods=['POST'])
def add_mac_address(asset_id):
    if require_login():
        return require_login()

    data = request.get_json()
    data['operator'] = get_current_user()

    if not data.get('mac'):
        return jsonify({'code': 400, 'message': 'mac is required'}), 400

    mac, error = AssetService.add_mac_address(asset_id, data)
    if error:
        return jsonify({'code': 404, 'message': error}), 404

    return jsonify({
        'code': 200,
        'data': mac.to_dict()
    })

@asset_bp.route('/mac/<mac_id>', methods=['DELETE'])
def delete_mac_address(mac_id):
    if require_login():
        return require_login()

    operator = request.args.get('operator', get_current_user())

    result, error = AssetService.delete_mac_address(mac_id, operator)
    if error:
        return jsonify({'code': 404, 'message': error}), 404

    return jsonify({
        'code': 200,
        'message': 'MAC address deleted successfully'
    })

@asset_bp.route('/mac/<mac_id>', methods=['PUT'])
def update_mac_address(mac_id):
    if require_login():
        return require_login()

    data = request.get_json()
    operator = data.get('operator', get_current_user())

    mac, error = AssetService.update_mac_address(mac_id, data, operator)
    if error:
        return jsonify({'code': 404, 'message': error}), 404

    return jsonify({
        'code': 200,
        'data': mac.to_dict()
    })

@asset_bp.route('/assets/import/template', methods=['GET'])
def download_import_template():
    if require_login():
        return require_login()

    data = {
        '机器型号': ['联想 ThinkPad X1 Carbon'],
        '机器类型': ['笔记本'],
        '资产编号': [''],
        'MAC地址(格式:MAC,IP,MAC,IP)': ['001A2B3C4D5E,192.168.1.100,001A2B3C4D5F,192.168.1.101'],
        '使用人': [''],
        'CPU': ['Intel i7-1165G7'],
        '内存': ['16GB'],
        '硬盘': ['512GB SSD'],
        '序列号': [''],
        '是否报废(填是则报废)': [''],
        '备注': ['']
    }
    
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='资产导入模板')
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='资产导入模板.xlsx'
    )

@asset_bp.route('/assets/import', methods=['POST'])
def import_assets():
    if require_login():
        return require_login()

    if not session.get('is_admin'):
        return jsonify({'code': 403, 'message': '只有管理员可以导入资产'}), 403

    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '请上传文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 400, 'message': '请选择文件'}), 400

    try:
        df = pd.read_excel(file)
        df.columns = [col.strip() for col in df.columns]

        required_columns = ['机器型号', '机器类型']
        for col in required_columns:
            if col not in df.columns:
                return jsonify({'code': 400, 'message': f'缺少必填列: {col}'}), 400

        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }

        for index, row in df.iterrows():
            try:
                row_idx = index + 2

                machine_model = str(row['机器型号']).strip()
                machine_type = str(row['机器类型']).strip()

                if not machine_model or machine_model == 'nan':
                    results['failed'] += 1
                    results['errors'].append(f'第 {row_idx} 行: 机器型号不能为空')
                    continue

                if not machine_type or machine_type == 'nan':
                    results['failed'] += 1
                    results['errors'].append(f'第 {row_idx} 行: 机器类型不能为空')
                    continue

                asset_code = str(row['资产编号']).strip() if '资产编号' in df.columns and pd.notna(row['资产编号']) else None
                if asset_code == 'nan':
                    asset_code = None

                mac_addresses = []
                
                mac_col = 'MAC地址(格式:MAC,IP,MAC,IP)'
                if mac_col not in df.columns:
                    mac_col = 'MAC地址'
                
                if mac_col in df.columns and pd.notna(row[mac_col]):
                    mac_str = str(row[mac_col]).strip()
                    if mac_str and mac_str != 'nan':
                        parts = [p.strip() for p in mac_str.split(',')]
                        i = 0
                        while i < len(parts):
                            mac = parts[i].upper().replace(':', '').replace('-', '').replace('.', '')
                            if mac and len(mac) == 12:
                                ip = None
                                if i + 1 < len(parts):
                                    ip = parts[i + 1].strip()
                                    if not ip:
                                        ip = None
                                mac_addresses.append({'mac': mac, 'ip': ip, 'remark': '有线'})
                            i += 2
                
                user_name = None
                if '使用人' in df.columns and pd.notna(row['使用人']):
                    user_name_str = str(row['使用人']).strip()
                    if user_name_str and user_name_str != 'nan':
                        user_name = user_name_str
                
                is_retired = False
                if '是否报废(填是则报废)' in df.columns and pd.notna(row['是否报废(填是则报废)']):
                    retired_str = str(row['是否报废(填是则报废)']).strip()
                    if retired_str in ['是', 'yes', 'true', '1']:
                        is_retired = True
                
                data = {
                    'machine_model': machine_model,
                    'machine_type': machine_type,
                    'asset_code': asset_code,
                    'mac_addresses': mac_addresses,
                    'user_name': user_name,
                    'is_retired': is_retired,
                    'cpu': str(row['CPU']).strip() if 'CPU' in df.columns and pd.notna(row['CPU']) and str(row['CPU']) != 'nan' else None,
                    'memory': str(row['内存']).strip() if '内存' in df.columns and pd.notna(row['内存']) and str(row['内存']) != 'nan' else None,
                    'disk': str(row['硬盘']).strip() if '硬盘' in df.columns and pd.notna(row['硬盘']) and str(row['硬盘']) != 'nan' else None,
                    'serial_number': str(row['序列号']).strip() if '序列号' in df.columns and pd.notna(row['序列号']) and str(row['序列号']) != 'nan' else None,
                    'remark': str(row['备注']).strip() if '备注' in df.columns and pd.notna(row['备注']) and str(row['备注']) != 'nan' else None,
                    'operator': get_current_user()
                }

                AssetService.create_asset(data)
                results['success'] += 1

            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f'第 {index + 2} 行: {str(e)}')

        return jsonify({
            'code': 200,
            'data': results
        })

    except Exception as e:
        return jsonify({'code': 500, 'message': f'文件解析失败: {str(e)}'}), 500
