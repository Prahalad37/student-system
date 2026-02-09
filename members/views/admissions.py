"""Admission / enquiry CRM - list, add, edit, convert to student."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_POST

from ..models import AdmissionEnquiry, Member, ClassRoom
from ..utils import get_current_school
from ..utils.role_guards import require_roles


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def enquiry_list(request):
    """List enquiries with optional status filter."""
    school = get_current_school(request)
    if not school:
        return render(request, "404.html", status=404)
    status_filter = request.GET.get("status", "")
    qs = AdmissionEnquiry.objects.filter(school=school).order_by("-created_at")
    if status_filter:
        qs = qs.filter(status=status_filter)
    status_counts = [
        (s, AdmissionEnquiry.objects.filter(school=school, status=s).count())
        for s in ["New", "Contacted", "Visited", "Admitted", "Lost"]
    ]
    return render(
        request,
        "enquiry_list.html",
        {"enquiries": qs, "status_filter": status_filter, "status_counts": status_counts, "status_choices": AdmissionEnquiry.STATUS_CHOICES},
    )


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def enquiry_add(request):
    school = get_current_school(request)
    if not school:
        return render(request, "404.html", status=404)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        if name and phone:
            AdmissionEnquiry.objects.create(
                school=school,
                name=name,
                phone=phone,
                email=request.POST.get("email", "").strip() or None,
                class_applying=request.POST.get("class_applying", "").strip(),
                source=request.POST.get("source", "").strip(),
                status=request.POST.get("status", "New"),
                notes=request.POST.get("notes", "").strip(),
            )
            messages.success(request, "Enquiry added.")
            return redirect("enquiry_list")
        messages.error(request, "Name and phone are required.")
    return render(request, "enquiry_form.html", {"enquiry": None, "status_choices": AdmissionEnquiry.STATUS_CHOICES})


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def enquiry_edit(request, pk):
    school = get_current_school(request)
    if not school:
        return render(request, "404.html", status=404)
    enquiry = get_object_or_404(AdmissionEnquiry, pk=pk, school=school)
    if request.method == "POST":
        enquiry.name = request.POST.get("name", enquiry.name).strip()
        enquiry.phone = request.POST.get("phone", enquiry.phone).strip()
        enquiry.email = request.POST.get("email", "").strip() or None
        enquiry.class_applying = request.POST.get("class_applying", "").strip()
        enquiry.source = request.POST.get("source", "").strip()
        enquiry.status = request.POST.get("status", enquiry.status)
        enquiry.notes = request.POST.get("notes", "").strip()
        enquiry.save()
        messages.success(request, "Enquiry updated.")
        return redirect("enquiry_list")
    return render(request, "enquiry_form.html", {"enquiry": enquiry, "status_choices": AdmissionEnquiry.STATUS_CHOICES})


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def enquiry_convert(request, pk):
    """Redirect to New Admission with enquiry data pre-filled (via query params or session)."""
    school = get_current_school(request)
    if not school:
        return render(request, "404.html", status=404)
    enquiry = get_object_or_404(AdmissionEnquiry, pk=pk, school=school)
    # Redirect to add student with query params so the form can pre-fill
    from urllib.parse import urlencode
    params = urlencode({
        "from_enquiry": "1",
        "name": f"{enquiry.name}",
        "phone": enquiry.phone,
        "email": enquiry.email or "",
        "class_applying": enquiry.class_applying,
    })
    return redirect(f"{reverse('add')}?{params}")


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
@require_POST
def enquiry_change_status(request, pk):
    school = get_current_school(request)
    if not school:
        return render(request, "404.html", status=404)
    enquiry = get_object_or_404(AdmissionEnquiry, pk=pk, school=school)
    new_status = request.POST.get("status", "").strip()
    if new_status in ["New", "Contacted", "Visited", "Admitted", "Lost"]:
        enquiry.status = new_status
        enquiry.save()
        messages.success(request, f"Status set to {new_status}.")
    return redirect("enquiry_list")
