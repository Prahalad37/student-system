from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import Member
from .forms import MemberForm

# --- MAIN VIEWS ---

@login_required
def index(request):
    """
    Home page view.
    Displays a list of students and handles search functionality.
    """
    query = request.GET.get('query')  # Get search term from URL
    
    if query:
        # Search by Firstname OR Lastname (Case-insensitive)
        mymembers = Member.objects.filter(
            Q(firstname__icontains=query) | Q(lastname__icontains=query)
        )
    else:
        # Fetch all records if no search query
        mymembers = Member.objects.all()

    context = {
        'mymembers': mymembers,
    }
    return render(request, 'index.html', context)


@login_required
def add(request):
    """
    View to add a new student.
    Handles file upload for profile pictures.
    """
    if request.method == 'POST':
        # IMPORTANT: request.FILES is required to handle image uploads
        form = MemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Student added successfully! ✅")
            return redirect('index')
    else:
        form = MemberForm()
        
    return render(request, 'add.html', {'form': form})


@login_required
def update(request, id):
    """
    View to update an existing student's details.
    """
    member = Member.objects.get(id=id)
    
    if request.method == 'POST':
        # Pass 'instance' to update the specific record instead of creating a new one
        form = MemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "Student details updated! ✏️")
            return redirect('index')
    else:
        form = MemberForm(instance=member)
        
    return render(request, 'update.html', {'form': form, 'member': member})


@login_required
def delete(request, id):
    """
    View to delete a student record.
    """
    member = Member.objects.get(id=id)
    member.delete()
    messages.success(request, "Student deleted successfully. 🗑️")
    return redirect('index')


def details(request, id):
    """
    View to show detailed information of a single student.
    """
    mymember = Member.objects.get(id=id)
    return render(request, 'details.html', {'mymember': mymember})


# --- AUTHENTICATION SYSTEM ---

def login_user(request):
    """
    Handles user login.
    """
    if request.method == 'POST':
        user_name = request.POST['username']
        pass_word = request.POST['password']

        user = authenticate(request, username=user_name, password=pass_word)

        if user is not None:
            login(request, user)
            messages.success(request, "Welcome Back! Login Successful. 🔓")
            return redirect('index')
        else:
            messages.error(request, "Invalid Username or Password! ❌")
            return redirect('login')
            
    return render(request, 'login_user.html')


def logout_user(request):
    """
    Handles user logout.
    """
    logout(request)
    messages.success(request, "You have been logged out. 👋")
    return redirect('login')