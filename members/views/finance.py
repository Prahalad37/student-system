from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.db import transaction
from django.db.models import Sum, F
from django.contrib.auth.decorators import login_required
from xhtml2pdf import pisa
from ..models import Member, FeeTransaction, ClassRoom, FeeStructure, Expense
from ..forms import FeeCollectionForm, ExpenseForm
from ..utils import get_current_school
from ..utils.role_guards import require_roles
from ..services.finance import FinanceService  # Service layer for finance operations

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def fee_home(request):
    school = get_current_school(request)
    transactions = FeeTransaction.objects.filter(student__school=school).select_related('student').order_by('-payment_date', '-id')
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    class_filter = request.GET.get('class_id')
    mode_filter = request.GET.get('mode')

    if start_date: transactions = transactions.filter(payment_date__gte=start_date)
    if end_date: transactions = transactions.filter(payment_date__lte=end_date)
    if class_filter: transactions = transactions.filter(student__student_class__id=class_filter)
    if mode_filter: transactions = transactions.filter(payment_mode=mode_filter)

    total_collected = transactions.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    students = Member.objects.filter(school=school).annotate(balance=F('fee_total') - F('fee_paid')).order_by('-balance')
    tx_paginator = Paginator(transactions, 25)
    page_obj = tx_paginator.get_page(request.GET.get('page', 1))

    context = {
        'transactions': page_obj, 'page_obj': page_obj, 'total_collected': total_collected,
        'classes': ClassRoom.objects.filter(school=school), 'students': students
    }
    return render(request, 'fees.html', context)

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
def collect_fee(request):
    if request.method == "POST":
        school = get_current_school(request)
        form = FeeCollectionForm(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data['student_id']
            get_object_or_404(Member, id=student_id, school=school)
            FinanceService.collect_fee(
                school_id=school.id,
                student_id=student_id,
                amount=form.cleaned_data['amount'],
                mode=form.cleaned_data['mode'],
                date=form.cleaned_data['date']
            )
        return redirect('fee_home')
    return redirect('fee_home')

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
def fee_config(request):
    if request.method == "POST":
        school = get_current_school(request)
        FeeStructure.objects.create(
            school=school,
            class_room=get_object_or_404(ClassRoom, id=request.POST.get('class_id'), school=school),
            title=request.POST.get('title'), amount=request.POST.get('amount')
        )
    return redirect('fee_home')

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
def generate_monthly_dues(request):
    if request.method == "POST":
        school = get_current_school(request)
        fees_by_class = (
            FeeStructure.objects.filter(school=school)
            .values('class_room')
            .annotate(total=Sum('amount'))
        )
        for row in fees_by_class:
            if row['total'] and row['class_room']:
                Member.objects.filter(
                    school=school,
                    student_class_id=row['class_room']
                ).update(fee_total=F('fee_total') + row['total'])
    return redirect('fee_home')

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def receipt_pdf(request, id):
    school = get_current_school(request)
    t = get_object_or_404(FeeTransaction, id=id, student__school=school)
    template = get_template('receipt_pdf.html')
    school = t.student.school
    remaining_balance = (t.student.fee_total or 0) - (t.student.fee_paid or 0)
    html = template.render({'t': t, 'school': school, 'remaining_balance': remaining_balance})
    response = HttpResponse(content_type='application/pdf')
    pisa.CreatePDF(html, dest=response)
    return response


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def student_receipt_pdf(request, student_id: int):
    school = get_current_school(request)
    student = get_object_or_404(Member, id=student_id, school=school)
    t = FeeTransaction.objects.filter(student=student).order_by('-payment_date', '-id').first()
    if not t:
        return redirect('fee_home')
    return receipt_pdf(request, t.id)

@login_required
@require_roles("OWNER", "ADMIN")
def delete_fee(request, id):
    school = get_current_school(request)
    t = get_object_or_404(FeeTransaction, id=id, student__school=school)
    with transaction.atomic():
        Member.objects.filter(pk=t.student_id).update(
            fee_paid=F('fee_paid') - t.amount_paid
        )
        t.delete()
    return redirect('fee_home')

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def get_fee_amount(request):
    """Return due fee amount for a student (fee_total - fee_paid)."""
    student_id = request.GET.get('student_id')
    if not student_id:
        return JsonResponse({'error': 'student_id required'}, status=400)
    try:
        student_id = int(student_id)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'invalid student_id'}, status=400)
    school = get_current_school(request)
    student = get_object_or_404(Member, id=student_id, school=school)
    due_amount = (student.fee_total or 0) - (student.fee_paid or 0)
    return JsonResponse({'amount': str(max(due_amount, 0))})

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
def add_expense(request):
    school = get_current_school(request)
    form = ExpenseForm()
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.school = school
            obj.save()
            return redirect('add_expense')
    expenses = Expense.objects.filter(school=school).order_by('-id')
    return render(request, 'add_expense.html', {'expenses': expenses, 'form': form})