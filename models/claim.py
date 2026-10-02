from datetime import datetime

from models import db


class Claim(db.Model):
    __tablename__ = "claim"

    claim_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("item_report.item_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    claim_description = db.Column(db.Text, nullable=False)
    verification_information = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Pending")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by = db.Column(db.Integer, nullable=True)

    user = db.relationship("User", back_populates="claims")
    item_report = db.relationship("ItemReport", back_populates="claims")
