from datetime import datetime, timezone

from app.database import db


class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(100), nullable=False, index=True)
    metric_name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    severity_score = db.Column(db.Float, nullable=False)
    message = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="OPEN", index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "service": self.service,
            "metric_name": self.metric_name,
            "value": self.value,
            "severity": self.severity,
            "severity_score": self.severity_score,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
