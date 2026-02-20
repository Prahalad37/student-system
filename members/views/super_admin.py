"""
Super Admin Views - Software Owner Portal
Manages all schools in the multi-tenant system
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q
from members.models import School, Member
from django.utils.text import slugify
import random
import string


def is_super_admin(user):
    """Check if user is super admin"""
    return user.groups.filter(name='Super Admin').exists() or user.is_superuser


class SuperAdminLoginView(LoginView):
    """Custom login view for super admin"""
    template_name = 'super_admin/login.html'
    
    def get_success_url(self):
        return '/super-admin/dashboard/'


@login_required
@user_passes_test(is_super_admin, login_url='/super-admin/login/')
def super_admin_dashboard(request):
    """Super Admin Dashboard - Overview of all schools"""
    
    schools = School.objects.all()
    total_students = Member.objects.all().count()
    
    context = {
        'total_schools': schools.count(),
        'active_schools': schools.filter(is_active=True).count(),
        'demo_schools': schools.filter(is_demo=True).count(),
        'total_students': total_students,
        'schools': schools.order_by('-created_at')[:10],
    }
    
    return render(request, 'super_admin/dashboard.html', context)


@login_required
@user_passes_test(is_super_admin, login_url='/super-admin/login/')
def create_demo_school(request):
    """Create a demo school with sample data in 30 seconds"""
    
    if request.method == 'POST':
        school_name = request.POST.get('school_name', f"Demo School {random.randint(100, 999)}")
        
        # Generate unique code
        base_slug = slugify(school_name)
        slug = base_slug
        counter = 1
        while School.objects.filter(code=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Create school
        school = School.objects.create(
            name=school_name,
            address="123 Demo Street, Demo City",
            school_code=f"SCH{''.join(random.choices(string.digits, k=6))}",
            code=slug,
            is_demo=True,
            is_active=True,
            super_admin=request.user,
            primary_color='#4e73df',
        )
        
        messages.success(request, f'✅ Demo school "{school_name}" created successfully!')
        return redirect('super_admin:populate_demo_data', school_id=school.id)
    
    return render(request, 'super_admin/create_demo.html')


@login_required
@user_passes_test(is_super_admin, login_url='/super-admin/login/')
def populate_demo_data(request, school_id):
    """Populate demo school with sample data"""
    school = get_object_or_404(School, id=school_id, is_demo=True)
    
    # Import demo data generator
    from members.utils.demo_data_generator import DemoDataGenerator
    
    # Generate data
    generator = DemoDataGenerator(school)
    
    try:
        result = generator.generate_all()
        
        context = {
            'school': school,
            'admin_username': result['admin_username'],
            'admin_password': result['admin_password'],
            'school_url': f'/accounts/login/',
            'students_count': result['students_count'],
            'staff_count': result['staff_count'],
            'classes_count': result['classes_count'],
        }
        
        messages.success(request, f'✅ Demo data generated: {result["students_count"]} students, {result["staff_count"]} staff!')
        
    except Exception as e:
        messages.error(request, f'❌ Error generating demo data: {str(e)}')
        context = {
            'school': school,
            'admin_username': 'admin',
            'admin_password': 'demo123',
            'school_url': f'/accounts/login/',
            'error': str(e),
        }

    
    return render(request, 'super_admin/demo_credentials.html', context)


@login_required
@user_passes_test(is_super_admin, login_url='/super-admin/login/')
def school_list(request):
    """List all schools"""
    schools = School.objects.all().order_by('-created_at')
    
    return render(request, 'super_admin/school_list.html', {'schools': schools})


@login_required
@user_passes_test(is_super_admin, login_url='/super-admin/login/')
def toggle_school_status(request, school_id):
    """Toggle school active/inactive status"""
    school = get_object_or_404(School, id=school_id)
    school.is_active = not school.is_active
    school.save()
    
    status = "activated" if school.is_active else "deactivated"
    messages.success(request, f'School "{school.name}" has been {status}.')
    
    return redirect('super_admin:school_list')
