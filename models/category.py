from models import db


class Category(db.Model):
    __tablename__ = "category"

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=True, nullable=False)

    items = db.relationship("ItemReport", back_populates="category", cascade="all, delete-orphan")
