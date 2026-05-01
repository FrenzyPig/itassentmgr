from app import db
from app.models.asset import Asset
from app.models.mac_address import MacAddress
from app.models.usage_record import UsageRecord
from app.models.operation_log import OperationLog
from datetime import datetime
import time
import json

class AssetService:
    @staticmethod
    def generate_device_id():
        return str(int(time.time() * 1000))

    @staticmethod
    def generate_temp_code():
        today = datetime.now().strftime('%Y%m%d')
        prefix = f'NEW_{today}'

        existing = Asset.query.filter(Asset.asset_code.like(f'{prefix}%')).all()

        if not existing:
            return f'{prefix}_001'

        numbers = []
        for asset in existing:
            code = asset.asset_code
            if code.startswith(prefix):
                suffix = code[len(prefix)+1:]
                if suffix.isdigit():
                    numbers.append(int(suffix))

        if numbers:
            next_num = max(numbers) + 1
            return f'{prefix}_{next_num:03d}'
        else:
            return f'{prefix}_001'

    @staticmethod
    def create_asset(data):
        device_id = AssetService.generate_device_id()
        asset_code = data.get('asset_code')

        if not asset_code:
            asset_code = AssetService.generate_temp_code()

        user_name = data.get('user_name')
        is_retired = data.get('is_retired', False)
        
        if is_retired:
            asset_status = '报废'
        elif user_name:
            asset_status = '使用中'
        else:
            asset_status = '在库'

        asset = Asset(
            device_id=device_id,
            asset_code=asset_code,
            machine_model=data.get('machine_model'),
            machine_type=data.get('machine_type'),
            cpu=data.get('cpu'),
            memory=data.get('memory'),
            disk=data.get('disk'),
            serial_number=data.get('serial_number'),
            remark=data.get('remark'),
            status=asset_status
        )

        if asset_code.startswith('NEW_'):
            asset.temp_code = asset_code

        db.session.add(asset)
        db.session.flush()

        mac_addresses = data.get('mac_addresses', [])
        
        for mac_data in mac_addresses:
            mac = MacAddress(
                asset_id=asset.id,
                mac=mac_data.get('mac'),
                ip=mac_data.get('ip'),
                remark=mac_data.get('remark')
            )
            db.session.add(mac)

        operator = data.get('operator', 'system')

        if is_retired:
            usage_user = '报废'
        elif user_name:
            usage_user = user_name
        else:
            usage_user = '在库'
        
        network_info_list = []
        if not is_retired and user_name:
            for mac_data in mac_addresses:
                if mac_data.get('ip'):
                    network_info_list.append(f"{mac_data.get('mac')}[{mac_data.get('ip')}]")
        
        network_info = '|'.join(network_info_list) if network_info_list else None

        usage_record = UsageRecord(
            asset_id=asset.id,
            user_name=usage_user,
            start_time=datetime.utcnow(),
            operation_type='入库',
            operator=operator,
            ip_addresses=network_info
        )
        db.session.add(usage_record)

        log = OperationLog(
            asset_id=asset.id,
            device_id=asset.device_id,
            asset_code=asset.asset_code,
            operator=operator,
            action='创建资产',
            after_state=json.dumps(asset.to_simple_dict())
        )
        db.session.add(log)

        db.session.commit()
        return asset

    @staticmethod
    def update_asset(asset_id, data):
        asset = Asset.query.get(asset_id)
        if not asset:
            return None

        before_state = asset.to_simple_dict()

        if 'machine_model' in data:
            asset.machine_model = data['machine_model']
        if 'machine_type' in data:
            asset.machine_type = data['machine_type']
        if 'cpu' in data:
            asset.cpu = data['cpu']
        if 'memory' in data:
            asset.memory = data['memory']
        if 'disk' in data:
            asset.disk = data['disk']
        if 'serial_number' in data:
            asset.serial_number = data['serial_number']
        if 'remark' in data:
            asset.remark = data['remark']
        if 'asset_code' in data:
            asset.asset_code = data['asset_code']
            if not data['asset_code'].startswith('NEW_'):
                asset.temp_code = None

        operator = data.get('operator', 'system')

        log = OperationLog(
            asset_id=asset.id,
            device_id=asset.device_id,
            asset_code=asset.asset_code,
            operator=operator,
            action='更新资产',
            before_state=json.dumps(before_state),
            after_state=json.dumps(asset.to_simple_dict())
        )
        db.session.add(log)

        db.session.commit()
        return asset

    @staticmethod
    def claim_asset(asset_id, data):
        asset = Asset.query.get(asset_id)
        if not asset:
            return None, 'Asset not found'

        if asset.status == '报废':
            return None, 'Cannot claim retired asset'

        before_state = asset.to_simple_dict()

        active_record = UsageRecord.query.filter(
            UsageRecord.asset_id == asset_id,
            UsageRecord.end_time.is_(None)
        ).first()

        if active_record:
            active_record.end_time = datetime.utcnow()

        operator = data.get('operator', 'system')

        ip_data_list = data.get('ip_addresses', [])

        mac_addresses = MacAddress.query.filter_by(asset_id=asset_id).all()

        for mac in mac_addresses:
            ip_data = next((p for p in ip_data_list if p.get('mac_id') == mac.id), None)
            if ip_data:
                mac.ip = ip_data.get('ip') if ip_data.get('ip') != '0.0.0.0' else None
            else:
                mac.ip = None

        network_info_list = []
        for mac in mac_addresses:
            if mac.ip and mac.ip != '0.0.0.0':
                network_info_list.append(f'{mac.mac}[{mac.ip}]')

        network_info = '|'.join(network_info_list)

        new_record = UsageRecord(
            asset_id=asset_id,
            user_name=data.get('user_name'),
            start_time=datetime.utcnow(),
            operation_type='领用',
            operator=operator,
            ip_addresses=network_info
        )
        db.session.add(new_record)

        asset.status = '使用中'

        log = OperationLog(
            asset_id=asset.id,
            device_id=asset.device_id,
            asset_code=asset.asset_code,
            operator=operator,
            action='领用资产',
            before_state=json.dumps(before_state),
            after_state=json.dumps(asset.to_simple_dict())
        )
        db.session.add(log)

        db.session.commit()
        return asset, None

    @staticmethod
    def retire_asset(asset_id, data):
        asset = Asset.query.get(asset_id)
        if not asset:
            return None, 'Asset not found'

        before_state = asset.to_simple_dict()

        active_record = UsageRecord.query.filter(
            UsageRecord.asset_id == asset_id,
            UsageRecord.end_time.is_(None)
        ).first()

        operator = data.get('operator', 'system')

        if active_record:
            active_record.end_time = datetime.utcnow()

        asset.status = '报废'

        log = OperationLog(
            asset_id=asset.id,
            device_id=asset.device_id,
            asset_code=asset.asset_code,
            operator=operator,
            action='报废资产',
            before_state=json.dumps(before_state),
            after_state=json.dumps(asset.to_simple_dict())
        )
        db.session.add(log)

        db.session.commit()
        return asset, None

    @staticmethod
    def change_asset_user(asset_id, data):
        asset = Asset.query.get(asset_id)
        if not asset:
            return None, 'Asset not found'

        if asset.status == '报废':
            return None, 'Cannot change user of retired asset'

        before_state = asset.to_simple_dict()

        active_record = UsageRecord.query.filter(
            UsageRecord.asset_id == asset_id,
            UsageRecord.end_time.is_(None)
        ).first()

        operator = data.get('operator', 'system')

        ip_data_list = data.get('ip_addresses', [])

        mac_addresses = MacAddress.query.filter_by(asset_id=asset_id).all()

        for mac in mac_addresses:
            ip_data = next((p for p in ip_data_list if p.get('mac_id') == mac.id), None)
            if ip_data:
                mac.ip = ip_data.get('ip') if ip_data.get('ip') != '0.0.0.0' else None
            else:
                mac.ip = None

        network_info_list = []
        for mac in mac_addresses:
            if mac.ip and mac.ip != '0.0.0.0':
                network_info_list.append(f'{mac.mac}[{mac.ip}]')

        network_info = '|'.join(network_info_list)

        if active_record:
            active_record.end_time = datetime.utcnow()

        new_record = UsageRecord(
            asset_id=asset_id,
            user_name=data.get('user_name'),
            start_time=datetime.utcnow(),
            operation_type='领用',
            operator=operator,
            ip_addresses=network_info
        )
        db.session.add(new_record)

        log = OperationLog(
            asset_id=asset.id,
            device_id=asset.device_id,
            asset_code=asset.asset_code,
            operator=operator,
            action='更换使用人',
            before_state=json.dumps(before_state),
            after_state=json.dumps(asset.to_simple_dict())
        )
        db.session.add(log)

        db.session.commit()
        return asset, None

    @staticmethod
    def return_to_storage(asset_id, data):
        asset = Asset.query.get(asset_id)
        if not asset:
            return None, 'Asset not found'

        before_state = asset.to_simple_dict()

        active_record = UsageRecord.query.filter(
            UsageRecord.asset_id == asset_id,
            UsageRecord.end_time.is_(None)
        ).first()

        operator = data.get('operator', 'system')

        if active_record:
            active_record.end_time = datetime.utcnow()

        new_record = UsageRecord(
            asset_id=asset_id,
            user_name='在库',
            start_time=datetime.utcnow(),
            operation_type='入库',
            operator=operator
        )
        db.session.add(new_record)

        asset.status = '在库'

        mac_addresses = MacAddress.query.filter_by(asset_id=asset_id).all()
        for mac in mac_addresses:
            mac.ip = None

        log = OperationLog(
            asset_id=asset.id,
            device_id=asset.device_id,
            asset_code=asset.asset_code,
            operator=operator,
            action='退回入库',
            before_state=json.dumps(before_state),
            after_state=json.dumps(asset.to_simple_dict())
        )
        db.session.add(log)

        db.session.commit()
        return asset, None

    @staticmethod
    def add_mac_address(asset_id, data):
        asset = Asset.query.get(asset_id)
        if not asset:
            return None, 'Asset not found'

        mac = MacAddress(
            asset_id=asset_id,
            mac=data.get('mac'),
            ip=data.get('ip'),
            remark=data.get('remark')
        )
        db.session.add(mac)

        operator = data.get('operator', 'system')
        log = OperationLog(
            asset_id=asset_id,
            device_id=asset.device_id,
            asset_code=asset.asset_code,
            operator=operator,
            action='添加MAC地址',
            after_state=json.dumps({'mac': data.get('mac'), 'ip': data.get('ip'), 'remark': data.get('remark')})
        )
        db.session.add(log)

        db.session.commit()
        return mac, None

    @staticmethod
    def delete_mac_address(mac_id, operator='system'):
        mac = MacAddress.query.get(mac_id)
        if not mac:
            return None, 'MAC address not found'

        asset = Asset.query.get(mac.asset_id)
        asset_id = mac.asset_id

        log = OperationLog(
            asset_id=asset_id,
            device_id=asset.device_id if asset else None,
            asset_code=asset.asset_code if asset else None,
            operator=operator,
            action='删除MAC地址',
            before_state=json.dumps({'mac': mac.mac, 'ip': mac.ip, 'remark': mac.remark})
        )
        db.session.add(log)

        db.session.delete(mac)
        db.session.commit()
        return True, None

    @staticmethod
    def update_mac_address(mac_id, data, operator='system'):
        mac = MacAddress.query.get(mac_id)
        if not mac:
            return None, 'MAC address not found'

        asset = Asset.query.get(mac.asset_id)

        before_state = {'mac': mac.mac, 'ip': mac.ip, 'remark': mac.remark}
        mac.mac = data.get('mac', mac.mac)
        mac.ip = data.get('ip', mac.ip)
        mac.remark = data.get('remark', mac.remark)

        active_record = UsageRecord.query.filter(
            UsageRecord.asset_id == mac.asset_id,
            UsageRecord.end_time.is_(None)
        ).first()

        if active_record:
            old_network_info = active_record.ip_addresses or ''

            mac_addresses = MacAddress.query.filter_by(asset_id=mac.asset_id).all()

            new_network_info_list = []
            for m in mac_addresses:
                if m.ip and m.ip != '0.0.0.0':
                    new_network_info_list.append(f'{m.mac}[{m.ip}]')

            new_network_info = '|'.join(new_network_info_list)

            if old_network_info != new_network_info:
                active_record.end_time = datetime.utcnow()

                new_record = UsageRecord(
                    asset_id=mac.asset_id,
                    user_name=active_record.user_name,
                    start_time=datetime.utcnow(),
                    operation_type='修改',
                    operator=operator,
                    ip_addresses=new_network_info
                )
                db.session.add(new_record)

        log = OperationLog(
            asset_id=mac.asset_id,
            device_id=asset.device_id if asset else None,
            asset_code=asset.asset_code if asset else None,
            operator=operator,
            action='更新MAC地址',
            before_state=json.dumps(before_state),
            after_state=json.dumps({'mac': mac.mac, 'ip': mac.ip, 'remark': mac.remark})
        )
        db.session.add(log)

        db.session.commit()
        return mac, None

    @staticmethod
    def delete_asset(asset_id, operator='system'):
        asset = Asset.query.get(asset_id)
        if not asset:
            return None, 'Asset not found'

        log = OperationLog(
            asset_id=asset_id,
            device_id=asset.device_id,
            asset_code=asset.asset_code,
            operator=operator,
            action='删除资产',
            before_state=json.dumps(asset.to_simple_dict())
        )
        db.session.add(log)

        db.session.delete(asset)
        db.session.commit()
        return True, None

    @staticmethod
    def get_pending_assets():
        return Asset.query.filter(
            Asset.temp_code.isnot(None)
        ).all()
