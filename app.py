from flask import Flask
from flask_login import LoginManager

from config import Config
from models import db
from routes.main import main_bp
from services.seed import seed_database

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    from models.user import User

    return db.session.get(User, int(user_id))


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Please log in to continue."
    login_manager.login_message_category = "info"

    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        seed_database()

    @app.errorhandler(404)
    def handle_404(_error):
        return _render_error_page("Page not found", 404)

    @app.errorhandler(403)
    def handle_403(_error):
        return _render_error_page("You don't have permission to access this page.", 403)

    @app.errorhandler(500)
    def handle_500(_error):
        return _render_error_page("Something went wrong. Please try again.", 500)

    def _render_error_page(message, status_code):
        from flask import render_template

        return render_template(f"errors/{status_code}.html", message=message), status_code

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
