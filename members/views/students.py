from datetime import date
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden, JsonResponse
from ..models import Member, ClassRoom, ExamScore, Attendance, UserProfile, TransportRoute, StudentTransport
from ..utils import get_current_school
from ..validators import validate_image_file, validate_document_file
from ..utils.role_guards import require_roles

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def all_students(request):
    school = get_current_school(request)
    qs = Member.objects.select_related('school', 'student_class').filter(school=school).order_by('firstname')
    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'all_students.html', {'page_obj': page_obj, 'mymembers': page_obj})

@login_required
@require_roles("OWNER", "ADMIN")
def create_student_login(request, id):
    """Create a user account for a student to access the portal."""
    school = get_current_school(request)
    student = get_object_or_404(Member, id=id, school=school)
    if UserProfile.objects.filter(member=student).exists():
        messages.warning(request, "This student already has a login.")
        return redirect("student_profile", id=id)

    username = (student.admission_no or f"stu_{student.id}").strip().lower().replace(" ", "_")
    if User.objects.filter(username=username).exists():
        username = f"stu_{student.id}"

    from django.contrib.auth import get_user_model
    User = get_user_model()
    password = User.objects.make_random_password(length=8)
    user = User.objects.create_user(
        username=username,
        password=password,
        email=student.email or f"{username}@student.local",
    )
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.school = school
    profile.role = "STUDENT"
    profile.member = student
    profile.save()

    messages.success(request, f"Login created. Username: {username} | Temp password: {password} (share securely)")
    return redirect("student_profile", id=id)


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def student_profile(request, id):
    """
    Detailed view for a single student including exam and attendance stats.
    """
    school = get_current_school(request)
    student = get_object_or_404(Member.objects.select_related('school', 'student_class'), id=id, school=school)
    
    # Related data
    exams = ExamScore.objects.filter(student=student).order_by('-id')
    attendance_list = Attendance.objects.filter(student=student).order_by('-date')
    
    total_days = attendance_list.count()
    present_days = attendance_list.filter(status='Present').count()
    
    # Calculate percentage safely
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    due_amount = (student.fee_total or 0) - (student.fee_paid or 0)
    student.due_amount = due_amount

    has_login = UserProfile.objects.filter(member=student).exists()

    context = {
        'student': student,
        'exams': exams,
        'total_days': total_days,
        'present_days': present_days,
        'attendance_percent': round(attendance_percentage, 2),
        'has_login': has_login,
    }
    return render(request, 'student_profile.html', context)


@login_required
@require_roles("OWNER", "ADMIN", "TEACHER", "STAFF")
def add(request):
    from ..models import TransportRoute
    school = get_current_school(request)
    routes = TransportRoute.objects.filter(school=school).order_by('route_name')
    return render(request, 'add.html', {'routes': routes})


@login_required
@require_roles("OWNER", "ADMIN", "TEACHER", "STAFF")
def addrecord(request):
    if request.method != "POST":
        return redirect('add')

    school = get_current_school(request)

    class_name = (request.POST.get('student_class') or '').strip()
    section_name = (request.POST.get('section') or 'A').strip() or 'A'
    class_obj = None
    if class_name:
        class_obj, _ = ClassRoom.objects.get_or_create(
            school=school,
            name=class_name,
            section=section_name,
        )

    profile_pic = None
    if request.FILES.get('file'):
        try:
            validate_image_file(request.FILES['file'])
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('add')
        fs = FileSystemStorage()
        filename = fs.save(request.FILES['file'].name, request.FILES['file'])
        profile_pic = filename

    # Validate document uploads
    doc_fields = ['birth_certificate', 'aadhaar_card', 'transfer_certificate', 'previous_marksheet', 'photo_id']
    for field in doc_fields:
        f = request.FILES.get(field)
        if f:
            try:
                validate_document_file(f)
            except ValidationError as e:
                messages.error(request, f"{field.replace('_', ' ').title()}: {e}")
                return redirect('add')

    joined_date = request.POST.get('joined_date')
    joined_date = joined_date or date.today().isoformat()

    transport_mode = request.POST.get('transport_mode') or 'Self'
    route_name_val = request.POST.get('route_name')
    transport_route_id = request.POST.get('transport_route_id')

    member = Member.objects.create(
        school=school,
        admission_no=request.POST.get('admission_no'),
        firstname=request.POST.get('first', '').strip(),
        lastname=request.POST.get('last', '').strip(),
        father_name=request.POST.get('father_name'),
        mobile_number=request.POST.get('mobile_number'),
        email=request.POST.get('email'),
        student_class=class_obj,
        roll_number=request.POST.get('roll_number'),
        gender=request.POST.get('gender') or 'Male',
        dob=request.POST.get('dob') or None,
        address=request.POST.get('address'),
        joined_date=joined_date,
        profile_pic=profile_pic,
        blood_group=request.POST.get('blood_group'),
        transport_mode=transport_mode,
        route_name=route_name_val,
        house_team=request.POST.get('house_team'),
        preferred_stream=request.POST.get('preferred_stream'),
        fee_total=request.POST.get('fee_total') or 0,
        fee_paid=request.POST.get('fee_paid') or 0,
        # Phase 1: Mother's Information
        mother_name=request.POST.get('mother_name'),
        mother_mobile=request.POST.get('mother_mobile'),
        mother_occupation=request.POST.get('mother_occupation'),
        father_occupation=request.POST.get('father_occupation'),
        # Phase 1: Government & Identity
        aadhaar_number=request.POST.get('aadhaar_number') or None,
        caste_category=request.POST.get('caste_category') or 'General',
        religion=request.POST.get('religion'),
        nationality=request.POST.get('nationality') or 'Indian',
        # Phase 1: Previous Education
        previous_school=request.POST.get('previous_school'),
        previous_class=request.POST.get('previous_class'),
        tc_number=request.POST.get('tc_number'),
        # Phase 1: Emergency Contact
        emergency_contact_person=request.POST.get('emergency_contact_person'),
        emergency_phone=request.POST.get('emergency_phone'),
        emergency_relationship=request.POST.get('emergency_relationship'),
        # Phase 1: Additional Contact
        whatsapp_number=request.POST.get('whatsapp_number'),
        # Phase 2: Medical Information
        known_allergies=request.POST.get('known_allergies'),
        chronic_conditions=request.POST.get('chronic_conditions'),
        vaccination_status=request.POST.get('vaccination_status'),
        family_doctor_name=request.POST.get('family_doctor_name'),
        family_doctor_phone=request.POST.get('family_doctor_phone'),
        special_needs=request.POST.get('special_needs'),
        # Phase 2: Family Financial
        annual_income=request.POST.get('annual_income') or None,
        parent_education=request.POST.get('parent_education'),
        # Phase 2: Guardian Information
        guardian_name=request.POST.get('guardian_name'),
        guardian_relationship=request.POST.get('guardian_relationship'),
        guardian_contact=request.POST.get('guardian_contact'),
        # Phase 2: Document Uploads
        birth_certificate=request.FILES.get('birth_certificate'),
        aadhaar_card=request.FILES.get('aadhaar_card'),
        transfer_certificate=request.FILES.get('transfer_certificate'),
        previous_marksheet=request.FILES.get('previous_marksheet'),
        photo_id=request.FILES.get('photo_id'),
        # Phase 2: Sibling Information
        sibling_in_school=request.POST.get('sibling_in_school') == 'true',
        sibling_details=request.POST.get('sibling_details'),
        # Phase 2: Additional Contacts
        alternate_email=request.POST.get('alternate_email'),
        permanent_address=request.POST.get('permanent_address'),
        # Phase 3: Consent & Permissions
        terms_consent=request.POST.get('terms_consent') == 'on',
        photo_permission=request.POST.get('photo_permission') == 'on',
        communication_consent=request.POST.get('communication_consent') == 'on',
    )

    if transport_mode == 'School Bus' and transport_route_id:
        try:
            route = TransportRoute.objects.get(id=int(transport_route_id), school=school)
            from decimal import Decimal
            StudentTransport.objects.create(
                school=school,
                student=member,
                route=route,
                pickup_point=request.POST.get('transport_pickup_point') or '',
                monthly_fee=Decimal(str(request.POST.get('transport_monthly_fee') or '0')),
            )
        except (ValueError, TransportRoute.DoesNotExist):
            pass

    return redirect('all_students')


@login_required
@require_roles("OWNER", "ADMIN", "TEACHER", "STAFF")
def update(request, id):
    school = get_current_school(request)
    mymember = get_object_or_404(Member, id=id, school=school)
    all_classes = ClassRoom.objects.filter(school=school).order_by('name', 'section')

    if request.method == "POST":
        mymember.admission_no = request.POST.get('admission_no')
        mymember.firstname = request.POST.get('first', '').strip()
        mymember.lastname = request.POST.get('last', '').strip()
        mymember.gender = request.POST.get('gender') or mymember.gender
        mymember.roll_number = request.POST.get('roll_number')
        mymember.joined_date = request.POST.get('joined_date') or mymember.joined_date
        mymember.dob = request.POST.get('dob') or None
        mymember.father_name = request.POST.get('father_name')
        mymember.mobile_number = request.POST.get('mobile_number')
        mymember.email = request.POST.get('email')
        mymember.address = request.POST.get('address')
        mymember.preferred_stream = request.POST.get('preferred_stream')
        mymember.house_team = request.POST.get('house_team')
        mymember.transport_mode = request.POST.get('transport_mode')
        mymember.route_name = request.POST.get('route_name')
        mymember.blood_group = request.POST.get('blood_group')
        mymember.medical_conditions = request.POST.get('medical_conditions')
        mymember.fee_total = request.POST.get('fee_total') or mymember.fee_total
        mymember.fee_paid = request.POST.get('fee_paid') or mymember.fee_paid

        class_id = request.POST.get('class_id')
        if class_id and str(class_id).isdigit():
            mymember.student_class = get_object_or_404(ClassRoom, id=int(class_id), school=school)

        if request.FILES.get('file'):
            try:
                validate_image_file(request.FILES['file'])
            except ValidationError as e:
                messages.error(request, str(e))
                return render(request, 'update.html', {'mymember': mymember, 'all_classes': all_classes})
            fs = FileSystemStorage()
            filename = fs.save(request.FILES['file'].name, request.FILES['file'])
            mymember.profile_pic = filename

        mymember.save()
        return redirect('student_profile', id=mymember.id)

    return render(request, 'update.html', {'mymember': mymember, 'all_classes': all_classes})


@login_required
@require_roles("OWNER", "ADMIN")
def delete(request, id):
    school = get_current_school(request)
    get_object_or_404(Member, id=id, school=school).delete()
    return redirect('all_students')


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def id_card(request, id):
    school = get_current_school(request)
    student = get_object_or_404(Member, id=id, school=school)
    return render(request, 'id_card.html', {'student': student, 'school': school})


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def check_admission_number(request):
    """
    AJAX endpoint to check if admission number already exists.
    Returns JSON: {"exists": true/false, "student_name": "..."}
    """
    admission_no = request.GET.get('admission_no', '').strip()
    
    if not admission_no:
        return JsonResponse({'exists': False})
    
    school = get_current_school(request)
    existing_student = Member.objects.filter(
        school=school,
        admission_no__iexact=admission_no  # Case-insensitive check
    ).first()
    
    if existing_student:
        return JsonResponse({
            'exists': True,
            'student_name': f"{existing_student.firstname} {existing_student.lastname}",
            'class': str(existing_student.student_class) if existing_student.student_class else 'N/A'
        })
    
    return JsonResponse({'exists': False})


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def admission_receipt_pdf(request, id):
    school = get_current_school(request)
    student = get_object_or_404(Member, id=id, school=school)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Admission_Receipt_{student.admission_no}.pdf"'

    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from django.http import HttpResponse

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # --- Header ---
    y = height - 50
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width / 2, y, "ABC SCHOOL") # Replace with school.name if available
    
    y -= 30
    p.setFont("Helvetica", 12)
    p.drawCentredString(width / 2, y, "Excellence in Education")
    p.drawCentredString(width / 2, y - 15, "123 School Road, City, State - 123456")
    
    y -= 40
    p.line(50, y, width - 50, y)
    
    # --- Title ---
    y -= 40
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, y, "ADMISSION CONFIRMATION RECEIPT")

    # --- Student Details ---
    y -= 50
    x_left = 70
    x_right = 350
    line_height = 25
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(x_left, y, "Student Information")
    y -= line_height
    p.line(x_left, y+5, 200, y+5) # Underline

    p.setFont("Helvetica", 12)
    
    labels = [
        ("Admission Number:", student.admission_no),
        ("Student Name:", f"{student.firstname} {student.lastname}"),
        ("Class & Section:", str(student.student_class) if student.student_class else "N/A"),
        ("Date of Birth:", str(student.dob) if student.dob else "N/A"),
        ("Gender:", student.gender),
        ("Father's Name:", student.father_name),
        ("Mobile Number:", student.mobile_number),
        ("Address:", student.address[:50] + "..." if student.address and len(student.address)>50 else student.address),
        ("Admission Date:", str(student.joined_date)),
    ]

    for label, value in labels:
        y -= line_height
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x_left, y, label)
        p.setFont("Helvetica", 10)
        p.drawString(x_left + 150, y, str(value or "N/A"))

    # --- Financial Details ---
    y_finance = height - 210
    
    y -= 40
    p.setFont("Helvetica-Bold", 12)
    p.drawString(x_left, y, "Fee Details")
    y -= line_height
    p.line(x_left, y+5, 150, y+5)

    p.setFont("Helvetica", 11)
    fee_data = [
        ("Total Fee:", f"Rs. {student.fee_total}"),
        ("Amount Paid:", f"Rs. {student.fee_paid}"),
        ("Balance Due:", f"Rs. {(student.fee_total or 0) - (student.fee_paid or 0)}"),
    ]

    for label, value in fee_data:
        y -= line_height
        p.drawString(x_left, y, label)
        p.drawString(x_left + 150, y, value)

    # --- Footer ---
    y = 100
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(x_left, y, "Authorized Signatory")
    p.drawString(width - 200, y, "Parent/Guardian Signature")
    
    p.line(x_left, y+10, x_left + 150, y+10)
    p.line(width - 200, y+10, width - 50, y+10)

    y -= 40
    p.setFont("Helvetica", 8)
    p.drawCentredString(width / 2, y, "This is a computer-generated receipt.")

    p.showPage()
    p.save()
    return response