from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app.extensions import csrf
from app.services.notification_service import NotificationService

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/notifications")
@login_required
def list_page():
    result = NotificationService.list_notifications(current_user.id)
    return render_template(
        "notifications/list.html",
        notifications=result.data if result.success else [],
    )


@notifications_bp.route("/api/notifications")
@login_required
def api_list():
    result = NotificationService.list_notifications(current_user.id)
    if result.success:
        return jsonify({"status": "success", "notifications": result.data})
    return jsonify({"status": "error", "message": result.error}), 400


@notifications_bp.route("/api/notifications/unread-count")
@login_required
def api_unread_count():
    result = NotificationService.unread_count(current_user.id)
    return jsonify(result.data if result.success else {"count": 0})


@notifications_bp.route("/api/notifications/<int:notification_id>/read", methods=["POST"])
@login_required
@csrf.exempt
def api_mark_read(notification_id):
    result = NotificationService.mark_read(current_user.id, notification_id)
    if result.success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": result.error}), 400


@notifications_bp.route("/api/notifications/read-all", methods=["POST"])
@login_required
@csrf.exempt
def api_mark_all_read():
    result = NotificationService.mark_all_read(current_user.id)
    if result.success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": result.error}), 400
