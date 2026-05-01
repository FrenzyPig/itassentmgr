from app import db
from app.utils.timezone import get_beijing_time, format_datetime
import uuid

class MacAddress(db.Model):
    __tablename__ = 'mac_addresses'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = db.Column(db.String(36), db.ForeignKey('assets.id'), nullable=False)
    mac = db.Column(db.String(17), nullable=False)
    ip = db.Column(db.String(45), nullable=True)
    remark = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=get_beijing_time)

    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'mac': self.mac,
            'ip': self.ip,
            'remark': self.remark,
            'created_at': format_datetime(self.created_at)
        }
