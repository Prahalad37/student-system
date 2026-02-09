"""Timetable / scheduling - view and edit by class or teacher."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Max

from ..models import School, ClassRoom, Subject, Staff, TimeSlot, TimetableEntry
from ..utils import get_current_school
from ..utils.role_guards import require_roles


@login_required
@require_roles("OWNER", "ADMIN", "TEACHER", "STAFF")
def timetable_view(request):
    """List timetable by class or by teacher (grid: days x slots)."""
    school = get_current_school(request)
    if not school:
        return render(request, "404.html", status=404)
    class_id = request.GET.get("class_id")
    teacher_id = request.GET.get("teacher_id")
    slots = TimeSlot.objects.filter(school=school).order_by("order", "start_time")
    entries = TimetableEntry.objects.filter(school=school).select_related(
        "class_room", "subject", "staff", "time_slot"
    )
    if class_id:
        entries = entries.filter(class_room_id=class_id)
    if teacher_id:
        entries = entries.filter(staff_id=teacher_id)

    # Build grid: rows = slots, cols = days 1..6
    days = [1, 2, 3, 4, 5, 6]
    entry_map = {(e.time_slot_id, e.day_of_week): e for e in entries}
    rows = []
    for slot in slots:
        row_entries = [entry_map.get((slot.id, d)) for d in days]
        rows.append((slot, row_entries))

    classes = ClassRoom.objects.filter(school=school).order_by("name", "section")
    teachers = Staff.objects.filter(school=school, is_active=True).order_by("first_name")
    return render(
        request,
        "timetable_view.html",
        {
            "rows": rows,
            "days": days,
            "classes": classes,
            "teachers": teachers,
            "selected_class_id": class_id,
            "selected_teacher_id": teacher_id,
        },
    )


@login_required
@require_roles("OWNER", "ADMIN")
def timetable_edit(request):
    """Add or edit timetable entries (manage slots + entries)."""
    school = get_current_school(request)
    if not school:
        return render(request, "404.html", status=404)
    slots = TimeSlot.objects.filter(school=school).order_by("order", "start_time")
    classes = ClassRoom.objects.filter(school=school).order_by("name", "section")
    subjects = Subject.objects.filter(school=school).order_by("name")
    staff_list = Staff.objects.filter(school=school, is_active=True).order_by("first_name")

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add_slot":
            from datetime import datetime
            start = request.POST.get("start_time")
            end = request.POST.get("end_time")
            if start and end:
                try:
                    start_t = datetime.strptime(start, "%H:%M").time()
                    end_t = datetime.strptime(end, "%H:%M").time()
                except (ValueError, TypeError):
                    start_t = end_t = None
                if start_t and end_t:
                    order = (TimeSlot.objects.filter(school=school).aggregate(m=Max("order"))["m"] or 0) + 1
                    TimeSlot.objects.create(school=school, start_time=start_t, end_time=end_t, order=order)
                messages.success(request, "Time slot added.")
            return redirect("timetable_edit")
        if action == "add_entry":
            class_id = request.POST.get("class_room_id")
            subject_id = request.POST.get("subject_id")
            staff_id = request.POST.get("staff_id") or None
            day = request.POST.get("day_of_week")
            slot_id = request.POST.get("time_slot_id")
            if class_id and subject_id and day and slot_id:
                class_room = get_object_or_404(ClassRoom, id=class_id, school=school)
                subject = get_object_or_404(Subject, id=subject_id, school=school)
                slot = get_object_or_404(TimeSlot, id=slot_id, school=school)
                staff = get_object_or_404(Staff, id=staff_id, school=school) if staff_id else None
                # Conflict: same class same day same slot
                if TimetableEntry.objects.filter(school=school, class_room=class_room, day_of_week=int(day), time_slot=slot).exists():
                    messages.error(request, "This class already has an entry for this day and slot.")
                else:
                    TimetableEntry.objects.create(
                        school=school,
                        class_room=class_room,
                        subject=subject,
                        staff=staff,
                        day_of_week=int(day),
                        time_slot=slot,
                    )
                    messages.success(request, "Entry added.")
            return redirect("timetable_edit")

    entries = TimetableEntry.objects.filter(school=school).select_related(
        "class_room", "subject", "staff", "time_slot"
    ).order_by("class_room__name", "day_of_week", "time_slot__order")
    return render(
        request,
        "timetable_edit.html",
        {"slots": slots, "classes": classes, "subjects": subjects, "staff_list": staff_list, "entries": entries},
    )


@login_required
@require_roles("OWNER", "ADMIN")
@require_POST
def timetable_delete_entry(request, entry_id):
    school = get_current_school(request)
    e = get_object_or_404(TimetableEntry, id=entry_id, school=school)
    e.delete()
    messages.success(request, "Entry removed.")
    return redirect("timetable_edit")
