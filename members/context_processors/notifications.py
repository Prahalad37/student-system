"""Expose notification count and recent notifications for navbar."""
from ..models import Notification


def notifications(request):
    if not getattr(request, "user", None) or not getattr(request.user, "is_authenticated", False):
        return {"unread_notification_count": 0, "recent_notifications": []}
    school = getattr(request, "school", None)
    if not school:
        return {"unread_notification_count": 0, "recent_notifications": []}
    qs = Notification.objects.filter(school=school, user=request.user).order_by("-created_at")[:8]
    unread_count = Notification.objects.filter(school=school, user=request.user, read=False).count()
    return {
        "unread_notification_count": unread_count,
        "recent_notifications": list(qs),
    }
