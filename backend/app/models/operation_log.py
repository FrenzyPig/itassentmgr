from app import db
from app.utils.timezone import get_beijing_time, to_beijing_time
import uuid
import json

def format_datetime(dt):
    if dt is None:
        return None
    return to_beijing_time(dt).strftime('%Y-%m-%d %H:%M:%S')

class OperationLog(db.Model):
    __tablename__ = 'operation_logs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = db.Column(db.String(36), db.ForeignKey('assets.id'))
    device_id = db.Column(db.String(17))
    asset_code = db.Column(db.String(100))
    operator = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    before_state = db.Column(db.Text)
    after_state = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_beijing_time)

    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'device_id': self.device_id,
            'asset_code': self.asset_code,
            'operator': self.operator,
            'action': self.action,
            'before_state': json.loads(self.before_state) if self.before_state else None,
            'after_state': json.loads(self.after_state) if self.after_state else None,
            'created_at': format_datetime(self.created_at)
        }
