from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from xhtml2pdf import pisa
from ..models import Staff, SalaryTransaction
from ..utils import get_current_school
from ..utils.role_guards import require_roles

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def staff_list(request):
    school = get_current_school(request)
    staff_qs = Staff.objects.filter(school=school, is_active=True)
    paginator = Paginator(staff_qs, 25)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    salary_history = SalaryTransaction.objects.select_related('staff').filter(school=school).order_by('-payment_date')[:50]
    
    context = {
        'staff_members': page_obj, 'page_obj': page_obj, 'salary_history': salary_history,
        'total_staff': staff_qs.count(),
        'monthly_payroll_est': staff_qs.aggregate(Sum('salary'))['salary__sum'] or 0
    }
    return render(request, 'hr_staff.html', context)

@login_required
@require_roles("OWNER", "ADMIN")
def add_staff(request):
    if request.method == "POST":
        school = get_current_school(request)
        Staff.objects.create(
            school=school, first_name=request.POST['first_name'], 
            last_name=request.POST['last_name'], phone=request.POST['phone'], 
            designation=request.POST['designation'], salary=request.POST['salary'], 
            join_date=request.POST['join_date']
        )
    return redirect('staff_list')

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
def pay_salary(request):
    if request.method == "POST":
        school = get_current_school(request)
        staff = get_object_or_404(Staff, id=request.POST.get('staff_id'), school=school)
        SalaryTransaction.objects.create(
            school=staff.school, staff=staff, amount_paid=request.POST.get('amount'), 
            month_year=request.POST.get('month_year'), payment_date=request.POST.get('payment_date'), 
            payment_mode=request.POST.get('mode')
        )
    return redirect('staff_list')

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def salary_slip_pdf(request, id):
    school = get_current_school(request)
    t = get_object_or_404(SalaryTransaction, id=id, school=school)
    template = get_template('salary_slip_pdf.html')
    html = template.render({'t': t, 'school': t.school})
    response = HttpResponse(content_type='application/pdf')
    pisa.CreatePDF(html, dest=response)
    return response