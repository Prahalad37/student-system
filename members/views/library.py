import xlwt
from datetime import date
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from ..models import Member, Book, LibraryTransaction, StudyMaterial
from ..utils import get_current_school
from ..utils.role_guards import require_roles
from ..validators import validate_document_file
from ..services.library import LibraryService  # Service Layer Import

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def library(request):
    school = get_current_school(request)
    books = Book.objects.filter(school=school).order_by('-id')
    transactions_qs = LibraryTransaction.objects.filter(school=school, status='Issued').select_related('student', 'book')
    paginator = Paginator(transactions_qs, 25)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    all_students = Member.objects.filter(school=school).order_by('firstname')

    context = {
        'books': books,
        'transactions': page_obj,
        'page_obj': page_obj,
        'total_books': books.count(),
        'issued_books': transactions_qs.count(), 
        'all_students': all_students
    }
    return render(request, 'library.html', context)

@login_required
@require_roles("OWNER", "ADMIN", "STAFF")
def add_book(request):
    if request.method == "POST":
        Book.objects.create(
            school=get_current_school(request),
            title=request.POST['title'], author=request.POST['author'],
            isbn=request.POST.get('isbn', ''), total_copies=int(request.POST['copies']),
            available_copies=int(request.POST['copies'])
        )
    return redirect('/library/')

@login_required
@require_roles("OWNER", "ADMIN", "STAFF", "TEACHER")
def issue_book(request):
    if request.method == "POST":
        try:
            school = get_current_school(request)
            student_id = request.POST.get('student_id')
            book_id = request.POST.get('book_id')
            due_date = request.POST.get('due_date')

            # Delegate to Service
            LibraryService.issue_book(school_id=school.id, student_id=student_id, book_id=book_id, due_date=due_date)
            
        except ValueError as e:
            return HttpResponse(f"Error: {str(e)}")
        except Exception:
            return HttpResponse("System Error: Could not issue book.")
            
    return redirect('/library/')

@login_required
@require_roles("OWNER", "ADMIN", "STAFF", "TEACHER")
def return_book(request, id):
    try:
        school = get_current_school(request)
        LibraryService.return_book(school_id=school.id, transaction_id=id)
    except Exception:
        pass 
    return redirect('/library/')

@login_required
@require_roles("OWNER", "ADMIN")
def delete_book(request, id):
    school = get_current_school(request)
    book = get_object_or_404(Book, id=id, school=school)
    if not LibraryTransaction.objects.filter(school=school, book=book, status='Issued').exists():
        book.delete()
    return redirect('/library/')

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def export_library_history(request):
    school = get_current_school(request)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Library_Report.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Library')
    columns = ['Student', 'Book', 'Issue Date', 'Due Date', 'Status', 'Fine']
    for col, name in enumerate(columns): ws.write(0, col, name)
    for row, t in enumerate(LibraryTransaction.objects.filter(school=school).select_related('student', 'book'), 1):
        ws.write(row, 0, f"{t.student.firstname} {t.student.lastname}")
        ws.write(row, 1, t.book.title)
        ws.write(row, 2, str(t.issue_date))
        ws.write(row, 3, str(t.due_date))
        ws.write(row, 4, t.status)
        ws.write(row, 5, t.fine_amount)
    wb.save(response)
    return response

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def digital_library(request): 
    school = get_current_school(request)
    if request.method == "POST":
        pdf_file = None
        if request.FILES.get('pdf_file'):
            try:
                validate_document_file(request.FILES['pdf_file'])
            except ValidationError as e:
                messages.error(request, str(e))
                materials = StudyMaterial.objects.filter(school=school).order_by('-id')
                return render(request, 'library.html', {'materials': materials})
            fs = FileSystemStorage()
            pdf_file = fs.save(request.FILES['pdf_file'].name, request.FILES['pdf_file'])
        StudyMaterial.objects.create(
            school=school,
            title=request.POST.get('title'), subject=request.POST.get('subject'), 
            class_name=request.POST.get('class_name'), video_link=request.POST.get('video_link'),
            pdf_file=pdf_file
        )
        return redirect('digital_library')
    materials = StudyMaterial.objects.filter(school=school).order_by('-id')
    return render(request, 'library.html', {'materials': materials})