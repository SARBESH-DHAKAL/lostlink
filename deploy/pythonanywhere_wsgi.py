import os
import sys

project_home = "/home/YOUR_USERNAME/lostlink"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ["SECRET_KEY"] = "REPLACE_WITH_A_RANDOM_SECRET_KEY"
os.environ["DEMO_ADMIN_EMAIL"] = "admin@lostlink.edu"
os.environ["DEMO_ADMIN_PASSWORD"] = "REPLACE_WITH_A_UNIQUE_ADMIN_PASSWORD"
os.environ["DATABASE_URL"] = f"sqlite:///{project_home}/database/lostlink.db"
os.environ["UPLOAD_FOLDER"] = f"{project_home}/uploads"
os.environ["SESSION_COOKIE_SECURE"] = "true"

from app import app as application