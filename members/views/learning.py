"""
Phase 2: Learning Hub - Study Materials & Video Library
"""
import re
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from ..models import StudyMaterial
from ..utils import get_current_school
from ..utils.role_guards import require_roles
from ..validators import validate_document_file


def _youtube_embed_url(url):
    """Convert YouTube watch URL to embed URL."""
    if not url:
        return None
    # Match youtube.com/watch?v=ID or youtu.be/ID
    m = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
    return f"https://www.youtube.com/embed/{m.group(1)}" if m else url


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def learning_hub(request):
    """Study Materials & Video Library - list and add."""
    school = get_current_school(request)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        subject = request.POST.get("subject", "").strip()
        class_name = request.POST.get("class_name", "").strip()
        video_link = request.POST.get("video_link", "").strip() or None

        pdf_file = None
        if request.FILES.get("pdf_file"):
            try:
                validate_document_file(request.FILES["pdf_file"])
            except ValidationError as e:
                messages.error(request, str(e))
            else:
                pdf_file = request.FILES["pdf_file"]

        if not title or not subject or not class_name:
            messages.error(request, "Title, Subject and Class are required.")
        elif not pdf_file and not video_link:
            messages.error(request, "Provide either a PDF file or a Video link.")
        else:
            material = StudyMaterial(
                school=school,
                title=title,
                subject=subject,
                class_name=class_name,
                video_link=video_link,
            )
            if pdf_file:
                material.pdf_file = pdf_file
            material.save()
            messages.success(request, f"Added: {material.title}")
            return redirect("learning_hub")

    # Filter by subject/class
    qs = StudyMaterial.objects.filter(school=school).order_by("-id")
    subject_filter = request.GET.get("subject", "").strip()
    class_filter = request.GET.get("class", "").strip()
    if subject_filter:
        qs = qs.filter(subject__icontains=subject_filter)
    if class_filter:
        qs = qs.filter(class_name__icontains=class_filter)

    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    # Add embed URL for templates
    materials = []
    for m in page_obj:
        materials.append({
            "obj": m,
            "embed_url": _youtube_embed_url(m.video_link) if m.video_link else None,
        })

    subjects = StudyMaterial.objects.filter(school=school).values_list("subject", flat=True).distinct().order_by("subject")
    classes = StudyMaterial.objects.filter(school=school).values_list("class_name", flat=True).distinct().order_by("class_name")

    return render(request, "learning_hub.html", {
        "materials": materials,
        "page_obj": page_obj,
        "subjects": subjects,
        "classes": classes,
        "subject_filter": subject_filter,
        "class_filter": class_filter,
    })


@login_required
@require_roles("STUDENT")
def student_portal(request):
    """Student panel - view study materials filtered by their class."""
    school = get_current_school(request)
    profile = getattr(request.user, "userprofile", None)
    member = profile.member if profile else None

    qs = StudyMaterial.objects.filter(school=school).order_by("-id")

    if member and member.student_class:
        class_name = member.student_class.name
        qs = qs.filter(class_name__icontains=class_name)

    materials = []
    for m in qs:
        materials.append({
            "obj": m,
            "embed_url": _youtube_embed_url(m.video_link) if m.video_link else None,
        })

    return render(request, "student_portal.html", {
        "materials": materials,
        "member": member,
    })


@login_required
@require_roles("OWNER", "ADMIN", "TEACHER")
def delete_study_material(request, id):
    """Delete a study material."""
    school = get_current_school(request)
    material = get_object_or_404(StudyMaterial, id=id, school=school)
    material.delete()
    messages.success(request, "Material deleted.")
    return redirect("learning_hub")
