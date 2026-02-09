"""In-app notifications - list, mark read, create (e.g. from dashboard)."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_GET
from django.contrib import messages

from ..models import Notification, Member, UserProfile, ClassRoom
from ..utils import get_current_school
from ..utils.role_guards import require_roles


@login_required
@require_GET
def notification_list(request):
    """Return recent notifications for current user (for navbar dropdown)."""
    school = get_current_school(request)
    if not school:
        return JsonResponse({"notifications": [], "unread_count": 0})
    qs = Notification.objects.filter(school=school, user=request.user).order_by("-created_at")[:15]
    notifications = [{"id": n.id, "title": n.title, "message": n.message[:100] if n.message else "", "read": n.read, "created_at": n.created_at.isoformat()} for n in qs]
    unread_count = Notification.objects.filter(school=school, user=request.user, read=False).count()
    return JsonResponse({"notifications": notifications, "unread_count": unread_count})


@login_required
def notification_mark_read(request, pk):
    """Mark one notification as read. Accepts GET (e.g. link click) and POST."""
    if request.method not in ("GET", "POST"):
        return JsonResponse({"error": "Method not allowed"}, status=405)
    school = get_current_school(request)
    if not school:
        return JsonResponse({"ok": False}, status=403)
    n = get_object_or_404(Notification, pk=pk, school=school, user=request.user)
    n.read = True
    n.save(update_fields=["read"])
    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.GET.get("ajax"):
        return JsonResponse({"ok": True})
    return redirect(request.GET.get("next", "index"))


@login_required
@require_POST
def notification_mark_all_read(request):
    """Mark all notifications as read for current user."""
    school = get_current_school(request)
    if not school:
        return JsonResponse({"ok": False}, status=403)
    Notification.objects.filter(school=school, user=request.user, read=False).update(read=True)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.GET.get("ajax"):
        return JsonResponse({"ok": True})
    return redirect(request.GET.get("next", "index"))


@login_required
@require_roles("OWNER", "ADMIN", "TEACHER")
def notification_send(request):
    """Create in-app notifications (and optionally email) for a class or all parents."""
    school = get_current_school(request)
    if not school:
        return redirect("index")
    if request.method != "POST":
        classes = ClassRoom.objects.filter(school=school).order_by("name")
        return render(request, "notification_send.html", {"classes": classes})
    title = request.POST.get("title", "").strip()
    message = request.POST.get("message", "").strip()
    target = request.POST.get("target", "all")  # all | class
    class_id = request.POST.get("class_id", "")
    if not title:
        messages.error(request, "Title is required.")
        return render(request, "notification_send.html", {"classes": ClassRoom.objects.filter(school=school).order_by("name")})
    # Find target users: parents (guardian_of) of students in class, or all users with school
    if target == "class" and class_id:
        student_ids = list(Member.objects.filter(school=school, student_class_id=class_id).values_list("id", flat=True))
        profiles = UserProfile.objects.filter(school=school, guardian_of__id__in=student_ids).distinct()
    else:
        profiles = UserProfile.objects.filter(school=school).exclude(role="STUDENT")
    user_ids = list(profiles.values_list("user_id", flat=True))
    for uid in user_ids:
        Notification.objects.create(school=school, user_id=uid, title=title, message=message)
    messages.success(request, f"Notification sent to {len(user_ids)} user(s).")
    return redirect("index")
