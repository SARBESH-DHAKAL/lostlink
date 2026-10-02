from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

from .category import Category
from .claim import Claim
from .item_report import ItemReport
from .notification import Notification
from .user import User
