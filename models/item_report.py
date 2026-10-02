from datetime import date, datetime

from models import db


class ItemReport(db.Model):
    __tablename__ = "item_report"

    item_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.category_id"), nullable=False)
    item_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    report_type = db.Column(db.String(20), nullable=False, default="Lost")
    location = db.Column(db.String(150), nullable=False)
    report_date = db.Column(db.Date, nullable=False, default=date.today)
    photo_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(30), nullable=False, default="Lost")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="reports")
    category = db.relationship("Category", back_populates="items")
    claims = db.relationship("Claim", back_populates="item_report", cascade="all, delete-orphan")
