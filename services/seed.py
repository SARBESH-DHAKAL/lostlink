import os
from datetime import date

from flask_bcrypt import generate_password_hash

from models import db
from models.category import Category
from models.item_report import ItemReport
from models.user import User


def seed_database():
    if Category.query.count() == 0:
        categories = [
            Category(category_name="Electronics"),
            Category(category_name="Documents"),
            Category(category_name="Books & Stationery"),
            Category(category_name="Wallets & Keys"),
            Category(category_name="Clothing"),
            Category(category_name="Accessories"),
            Category(category_name="Other"),
        ]
        db.session.add_all(categories)
        db.session.commit()

    if User.query.count() == 0:
        demo_user = User(
            full_name="Demo Student",
            email="demo@student.asmt.edu.np",
            password_hash=generate_password_hash("Password123!").decode("utf-8"),
            role="student",
        )
        db.session.add(demo_user)
        db.session.commit()

    admin_email = os.getenv("DEMO_ADMIN_EMAIL", "admin@lostlink.edu").lower()
    if not User.query.filter_by(email=admin_email).first():
        admin_user = User(
            full_name="LostLink Administrator",
            email=admin_email,
            password_hash=generate_password_hash(
                os.getenv("DEMO_ADMIN_PASSWORD", "Admin123!")
            ).decode("utf-8"),
            role="admin",
        )
        db.session.add(admin_user)
        db.session.commit()

    if ItemReport.query.count() == 0:
        demo_user = User.query.first()
        electronics = Category.query.filter_by(category_name="Electronics").first()
        stationery = Category.query.filter_by(category_name="Books & Stationery").first()
        wallets = Category.query.filter_by(category_name="Wallets & Keys").first()

        sample_reports = [
            ItemReport(
                user_id=demo_user.user_id,
                category_id=electronics.category_id,
                item_name="USB Drive",
                description="Black USB drive with a small blue sticker and a campus logo on it.",
                report_type="Lost",
                location="Computer Lab",
                report_date=date(2025, 9, 18),
                status="Lost",
            ),
            ItemReport(
                user_id=demo_user.user_id,
                category_id=stationery.category_id,
                item_name="Blue Notebook",
                description="A spiral blue notebook with handwritten engineering notes and a pen pocket.",
                report_type="Lost",
                location="College Library",
                report_date=date(2025, 9, 15),
                status="Lost",
            ),
            ItemReport(
                user_id=demo_user.user_id,
                category_id=wallets.category_id,
                item_name="Black Wallet",
                description="Black leather wallet found near the library entrance. Contains a student ID card sleeve.",
                report_type="Found",
                location="Library Entrance",
                report_date=date(2025, 9, 17),
                status="Found",
            ),
        ]
        db.session.add_all(sample_reports)
        db.session.commit()
