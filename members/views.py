from django.db.models import Q  # <--- Ye line top par add karein
from django.shortcuts import render, redirect
from .forms import MemberForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Member
from django.template import loader
from django.db.models import Q
from django.contrib import messages
# Authentication imports
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# 1. Home Page (List + Search)
@login_required
def index(request):
    query = request.GET.get('query') # Search box se text nikalo
    
    if query:
        # Agar user ne kuch search kiya hai (Firstname YA Lastname mein dhundo)
        mymembers = Member.objects.filter(
            Q(firstname__icontains=query) | Q(lastname__icontains=query)
        ).values()
    else:
        # Agar kuch search nahi kiya, toh sab dikhao
        mymembers = Member.objects.all().values()

    template = loader.get_template('index.html')
    context = {
        'mymembers': mymembers,
    }
    return HttpResponse(template.render(context, request))

# 2. Add Student
@login_required
def add(request):
    # Agar user Form bhar ke 'Submit' dabata hai (POST request)
    if request.method == 'POST':
        form = MemberForm(request.POST) # Form mein data bhara
        if form.is_valid():             # Check kiya ki data sahi hai ya nahi
            form.save()                 # Database mein save kiya
            messages.success(request, "Student successfully add ho gaya! 🎉")
            return HttpResponseRedirect(reverse('index'))
    
    # Agar user pehli baar page khol raha hai (GET request)
    else:
        form = MemberForm() # Khali form dikhao

    # HTML ko form bhejo
    return render(request, 'add.html', {'form': form})

# 3. Delete Student
@login_required
def delete(request, id):
    member = Member.objects.get(id=id)
    member.delete()
    messages.success(request, "Student delete kar diya gaya. 🗑️")
    return HttpResponseRedirect(reverse('index'))

# 4. Update/Edit Student
@login_required
def update(request, id):
    mymember = Member.objects.get(id=id)
    
    if request.method == 'POST':
        # 'instance=mymember' ka matlab hai: purana data form mein bhar do
        form = MemberForm(request.POST, instance=mymember)
        if form.is_valid():
            form.save()
            messages.success(request, "Record update ho gaya! ✏️")
            return HttpResponseRedirect(reverse('index'))
    else:
        # Jab page khule, toh purana data dikhao
        form = MemberForm(instance=mymember)

    return render(request, 'update.html', {'form': form})

# 5. Details View (Optional, agar use kar rahe hain)
def details(request, id):
    mymember = Member.objects.get(id=id)
    template = loader.get_template('details.html')
    context = {
        'mymember': mymember,
    }
    return HttpResponse(template.render(context, request))

# --- LOGIN SYSTEM ---

# 6. Login View
def login_user(request):
    if request.method == 'POST':
        user_name = request.POST['username']
        pass_word = request.POST['password']

        user = authenticate(request, username=user_name, password=pass_word)

        if user is not None:
            login(request, user)
            messages.success(request, "Welcome Back! Login Successful. 🔓")
            return HttpResponseRedirect(reverse('index'))
        else:
            messages.error(request, "Username ya Password galat hai! ❌")
            return HttpResponseRedirect(reverse('login'))
            
    return render(request, 'login_user.html')

# 7. Logout View
def logout_user(request):
    logout(request)
    messages.success(request, "Aap Logout ho gaye hain. 👋")
    return HttpResponseRedirect(reverse('login'))