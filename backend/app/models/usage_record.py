from app import db
from app.utils.timezone import get_beijing_time, to_beijing_time
import uuid

def format_datetime(dt):
    if dt is None:
        return None
    return to_beijing_time(dt).strftime('%Y-%m-%d %H:%M:%S')

class UsageRecord(db.Model):
    __tablename__ = 'usage_records'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = db.Column(db.String(36), db.ForeignKey('assets.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    operation_type = db.Column(db.String(50), nullable=False)
    operator = db.Column(db.String(100), nullable=False)
    ip_addresses = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_beijing_time)

    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'user_name': self.user_name,
            'start_time': format_datetime(self.start_time),
            'end_time': format_datetime(self.end_time),
            'operation_type': self.operation_type,
            'operator': self.operator,
            'ip_addresses': self.ip_addresses,
            'created_at': format_datetime(self.created_at)
        }
