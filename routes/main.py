import os
from datetime import date, datetime

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_from_directory, url_for
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from models import db
from models.category import Category
from models.claim import Claim
from models.item_report import ItemReport
from models.notification import Notification
from models.user import User

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    categories = Category.query.order_by(Category.category_name.asc()).all()
    recent_reports = ItemReport.query.order_by(ItemReport.created_at.desc()).limit(4).all()
    stats = {
        "items_reported": ItemReport.query.count(),
        "items_found": ItemReport.query.filter_by(report_type="Found").count(),
        "items_returned": ItemReport.query.filter_by(status="Returned").count(),
        "pending_claims": Claim.query.filter_by(status="Pending").count(),
    }
    return render_template(
        "index.html",
        categories=categories,
        recent_reports=recent_reports,
        stats=stats,
    )


@main_bp.route("/lost-items")
def lost_items():
    return render_item_list("Lost")


@main_bp.route("/found-items")
def found_items():
    return render_item_list("Found")


@main_bp.route("/items/<int:item_id>")
def item_detail(item_id):
    item = ItemReport.query.get_or_404(item_id)
    return render_template("items/detail.html", item=item)


@main_bp.route("/items/<int:item_id>/claim", methods=["GET", "POST"])
@login_required
def claim_item(item_id):
    item = ItemReport.query.get_or_404(item_id)

    if item.user_id == current_user.user_id:
        flash("You cannot claim your own item.", "info")
        return redirect(url_for("main.item_detail", item_id=item_id))

    form_data = {"claim_description": "", "verification_information": ""}
    errors = {}

    if request.method == "POST":
        form_data["claim_description"] = request.form.get("claim_description", "").strip()
        form_data["verification_information"] = request.form.get("verification_information", "").strip()

        if not form_data["claim_description"] or len(form_data["claim_description"]) < 10:
            errors["claim_description"] = "Please provide a clear claim description."
        if not form_data["verification_information"] or len(form_data["verification_information"]) < 10:
            errors["verification_information"] = "Please give matching verification details."

        if not errors:
            claim = Claim(
                item_id=item.item_id,
                user_id=current_user.user_id,
                claim_description=form_data["claim_description"],
                verification_information=form_data["verification_information"],
                status="Pending",
            )
            db.session.add(claim)
            db.session.commit()

            notification = Notification(
                user_id=current_user.user_id,
                message=f"Your claim for '{item.item_name}' is pending review.",
                notification_type="claim",
            )
            db.session.add(notification)
            db.session.commit()

            flash("Your claim has been submitted successfully.", "success")
            return redirect(url_for("main.dashboard"))

    return render_template("items/claim_form.html", item=item, form_data=form_data, errors=errors)


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form_data = {"email": "", "password": ""}
    errors = {}

    if request.method == "POST":
        form_data["email"] = request.form.get("email", "").strip()
        form_data["password"] = request.form.get("password", "")

        user = User.query.filter_by(email=form_data["email"].lower()).first()
        if not user or not check_password_hash(user.password_hash, form_data["password"]):
            errors["email"] = "Invalid email or password."
        else:
            login_user(user)
            flash("Welcome back!", "success")
            return redirect(request.args.get("next") or url_for("main.dashboard"))

    return render_template("auth/login.html", form_data=form_data, errors=errors)


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form_data = {"full_name": "", "email": "", "password": "", "confirm_password": ""}
    errors = {}

    if request.method == "POST":
        form_data["full_name"] = request.form.get("full_name", "").strip()
        form_data["email"] = request.form.get("email", "").strip()
        form_data["password"] = request.form.get("password", "")
        form_data["confirm_password"] = request.form.get("confirm_password", "")

        if not form_data["full_name"] or len(form_data["full_name"]) < 2:
            errors["full_name"] = "Please enter your full name."
        if not form_data["email"] or "@" not in form_data["email"]:
            errors["email"] = "Please enter a valid email address."
        elif User.query.filter_by(email=form_data["email"].lower()).first():
            errors["email"] = "An account with this email already exists."
        if not form_data["password"] or len(form_data["password"]) < 8:
            errors["password"] = "Password must be at least 8 characters long."
        if form_data["password"] != form_data["confirm_password"]:
            errors["confirm_password"] = "Passwords do not match."

        if not errors:
            user = User(
                full_name=form_data["full_name"],
                email=form_data["email"].lower(),
                password_hash=generate_password_hash(form_data["password"]).decode("utf-8"),
                role="student",
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Your account has been created successfully.", "success")
            return redirect(url_for("main.dashboard"))

    return render_template("auth/register.html", form_data=form_data, errors=errors)


@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    user_reports = ItemReport.query.filter_by(user_id=current_user.user_id).order_by(ItemReport.created_at.desc()).all()
    user_claims = Claim.query.filter_by(user_id=current_user.user_id).order_by(Claim.created_at.desc()).all()
    notifications = Notification.query.filter_by(user_id=current_user.user_id).order_by(Notification.created_at.desc()).all()
    return render_template("dashboard.html", user=current_user, reports=user_reports, claims=user_claims, notifications=notifications)


@main_bp.route("/admin/claims")
@login_required
def admin_claims():
    if current_user.role.lower() != "admin":
        abort(403)

    pending_claims = Claim.query.filter_by(status="Pending").order_by(Claim.created_at.asc()).all()
    return render_template("admin/claims.html", claims=pending_claims)


@main_bp.route("/admin/claims/<int:claim_id>/<decision>", methods=["POST"])
@login_required
def review_claim(claim_id, decision):
    if current_user.role.lower() != "admin":
        abort(403)
    if decision not in {"approve", "reject"}:
        abort(404)

    claim = Claim.query.get_or_404(claim_id)
    if claim.status != "Pending":
        flash("This claim has already been reviewed.", "info")
        return redirect(url_for("main.admin_claims"))

    now = datetime.utcnow()
    claim.status = "Approved" if decision == "approve" else "Rejected"
    claim.reviewed_at = now
    claim.reviewed_by = current_user.user_id
    if decision == "approve":
        claim.item_report.status = "Returned"

    db.session.add(Notification(
        user_id=claim.user_id,
        message=f"Your claim for '{claim.item_report.item_name}' was {claim.status.lower()}.",
        notification_type="claim",
    ))

    if decision == "approve":
        other_claims = Claim.query.filter(
            Claim.item_id == claim.item_id,
            Claim.claim_id != claim.claim_id,
            Claim.status == "Pending",
        ).all()
        for other_claim in other_claims:
            other_claim.status = "Rejected"
            other_claim.reviewed_at = now
            other_claim.reviewed_by = current_user.user_id
            db.session.add(Notification(
                user_id=other_claim.user_id,
                message=f"Your claim for '{claim.item_report.item_name}' was not approved because the item was returned to another claimant.",
                notification_type="claim",
            ))

    db.session.commit()
    flash(f"Claim {claim.status.lower()}.", "success")
    return redirect(url_for("main.admin_claims"))


@main_bp.route("/report-lost", methods=["GET", "POST"])
def report_lost():
    if not current_user.is_authenticated:
        flash("Please log in before submitting a report.", "info")
        return redirect(url_for("main.login", next=request.path))
    return handle_report_submission("Lost")


@main_bp.route("/report-found", methods=["GET", "POST"])
def report_found():
    if not current_user.is_authenticated:
        flash("Please log in before submitting a report.", "info")
        return redirect(url_for("main.login", next=request.path))
    return handle_report_submission("Found")


@main_bp.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


def handle_report_submission(report_type):
    categories = Category.query.order_by(Category.category_name.asc()).all()
    form_data = {
        "item_name": "",
        "description": "",
        "location": "",
        "report_date": "",
        "category": "",
    }
    errors = {}
    success_item = None

    if request.method == "POST":
        form_data.update({
            "item_name": request.form.get("item_name", "").strip(),
            "description": request.form.get("description", "").strip(),
            "location": request.form.get("location", "").strip(),
            "report_date": request.form.get("report_date", "").strip(),
            "category": request.form.get("category", "").strip(),
        })

        if not form_data["item_name"] or len(form_data["item_name"]) < 2:
            errors["item_name"] = "Item name is required."
        if not form_data["description"] or len(form_data["description"]) < 10:
            errors["description"] = "Please provide a detailed description."
        if not form_data["location"] or len(form_data["location"]) < 2:
            errors["location"] = "Location is required."
        if not form_data["report_date"]:
            errors["report_date"] = "Date is required."
        else:
            try:
                date.fromisoformat(form_data["report_date"])
            except ValueError:
                errors["report_date"] = "Please enter a valid date."

        category_obj = Category.query.filter_by(category_name=form_data["category"]).first() if form_data["category"] else None
        if not category_obj:
            errors["category"] = "Please select a valid category."

        photo_path = None
        uploaded_photo = request.files.get("photo")
        if uploaded_photo and uploaded_photo.filename:
            filename = secure_filename(uploaded_photo.filename)
            extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            allowed = {"png", "jpg", "jpeg", "webp"}
            if extension not in allowed:
                errors["photo"] = "Only JPG, PNG, and WEBP files are allowed."
            else:
                uploaded_photo.stream.seek(0, os.SEEK_END)
                size = uploaded_photo.stream.tell()
                uploaded_photo.stream.seek(0)
                if size > 5 * 1024 * 1024:
                    errors["photo"] = "Image must be smaller than 5MB."
                else:
                    upload_dir = current_app.config["UPLOAD_FOLDER"]
                    os.makedirs(upload_dir, exist_ok=True)
                    unique_name = f"{report_type.lower()}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                    saved_path = os.path.join(upload_dir, unique_name)
                    uploaded_photo.save(saved_path)
                    photo_path = f"/uploads/{unique_name}"

        if not errors:
            item = ItemReport(
                user_id=current_user.user_id,
                category_id=category_obj.category_id,
                item_name=form_data["item_name"],
                description=form_data["description"],
                report_type=report_type,
                location=form_data["location"],
                report_date=date.fromisoformat(form_data["report_date"]),
                photo_path=photo_path,
                status=report_type,
            )
            db.session.add(item)
            db.session.commit()
            success_item = item
            return render_template(
                "items/report_form.html",
                report_type=report_type,
                categories=categories,
                success=True,
                item=success_item,
                errors={},
                form_data={},
            )

    return render_template(
        "items/report_form.html",
        report_type=report_type,
        categories=categories,
        success=False,
        item=None,
        errors=errors,
        form_data=form_data,
    )


def render_item_list(report_type):
    keyword = request.args.get("keyword", "").strip()
    category_name = request.args.get("category", "").strip()
    location = request.args.get("location", "").strip()
    status = request.args.get("status", "").strip()
    sort = request.args.get("sort", "newest")

    query = ItemReport.query.filter_by(report_type=report_type)

    if keyword:
        query = query.filter(
            (ItemReport.item_name.ilike(f"%{keyword}%")) |
            (ItemReport.description.ilike(f"%{keyword}%"))
        )

    if category_name:
        category = Category.query.filter_by(category_name=category_name).first()
        if category:
            query = query.filter_by(category_id=category.category_id)

    if location:
        query = query.filter(ItemReport.location.ilike(f"%{location}%"))

    if status:
        query = query.filter_by(status=status)

    if sort == "oldest":
        query = query.order_by(ItemReport.report_date.asc(), ItemReport.created_at.asc())
    elif sort == "updated":
        query = query.order_by(ItemReport.created_at.desc())
    else:
        query = query.order_by(ItemReport.report_date.desc(), ItemReport.created_at.desc())

    categories = Category.query.order_by(Category.category_name.asc()).all()
    items = query.all()
    status_options = ["Lost", "Found", "Claim Pending", "Returned", "Closed"]

    return render_template(
        "items/list.html",
        items=items,
        report_type=report_type,
        categories=categories,
        status_options=status_options,
        keyword=keyword,
        category_name=category_name,
        location=location,
        status=status,
        sort=sort,
    )
