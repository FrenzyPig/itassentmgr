from app import db
from datetime import datetime
import uuid

def format_datetime(dt):
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')

class Asset(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = db.Column(db.String(17), unique=True, nullable=False)
    asset_code = db.Column(db.String(100), unique=True, nullable=False)
    temp_code = db.Column(db.String(100))
    machine_model = db.Column(db.String(200), nullable=False)
    machine_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='在库')
    cpu = db.Column(db.String(200))
    memory = db.Column(db.String(100))
    disk = db.Column(db.String(200))
    serial_number = db.Column(db.String(200))
    remark = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    mac_addresses = db.relationship('MacAddress', backref='asset', lazy=True, cascade='all, delete-orphan')
    usage_records = db.relationship('UsageRecord', backref='asset', lazy=True, cascade='all, delete-orphan')
    operation_logs = db.relationship('OperationLog', backref='asset', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'asset_code': self.asset_code,
            'temp_code': self.temp_code,
            'machine_model': self.machine_model,
            'machine_type': self.machine_type,
            'status': self.status,
            'cpu': self.cpu,
            'memory': self.memory,
            'disk': self.disk,
            'serial_number': self.serial_number,
            'remark': self.remark,
            'created_at': format_datetime(self.created_at),
            'updated_at': format_datetime(self.updated_at),
            'mac_addresses': [mac.to_dict() for mac in self.mac_addresses],
            'usage_records': [usage.to_dict() for usage in self.usage_records]
        }

    def to_simple_dict(self):
        from app.models.usage_record import UsageRecord

        result = {
            'id': self.id,
            'device_id': self.device_id,
            'asset_code': self.asset_code,
            'temp_code': self.temp_code,
            'machine_model': self.machine_model,
            'machine_type': self.machine_type,
            'status': self.status,
            'cpu': self.cpu,
            'memory': self.memory,
            'disk': self.disk,
            'serial_number': self.serial_number,
            'remark': self.remark,
            'created_at': format_datetime(self.created_at),
            'updated_at': format_datetime(self.updated_at),
            'user': '在库',
            'current_user': None
        }

        active_record = UsageRecord.query.filter(
            UsageRecord.asset_id == self.id,
            UsageRecord.end_time.is_(None)
        ).first()

        if active_record and active_record.user_name != '在库':
            result['user'] = active_record.user_name
            result['current_user'] = active_record.user_name

        return result
