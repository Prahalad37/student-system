from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Member
from django.template import loader
from django.db.models import Q
from django.contrib import messages
# Authentication imports
from django.contrib.auth import authenticate, login, logout

# 1. Home Page (List + Search)
def index(request):
    query = request.GET.get('q')
    if query:
        mymembers = Member.objects.filter(
            Q(firstname__icontains=query) | Q(lastname__icontains=query)
        )
    else:
        mymembers = Member.objects.all()
    
    context = {
        'mymembers': mymembers,
    }
    return render(request, 'index.html', context)

# 2. Add Student
def add(request):
    if request.method == 'POST':
        x = request.POST['first']
        y = request.POST['last']
        member = Member(firstname=x, lastname=y)
        member.save()
        messages.success(request, "Student successfully add ho gaya! 🎉")
        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, 'add.html')

# 3. Delete Student
def delete(request, id):
    member = Member.objects.get(id=id)
    member.delete()
    messages.success(request, "Student delete kar diya gaya. 🗑️")
    return HttpResponseRedirect(reverse('index'))

# 4. Update/Edit Student
def update(request, id):
    mymember = Member.objects.get(id=id) # Database se student nikala
    template = loader.get_template('update.html')
    context = {
        'mymember': mymember, # <-- Yahan 's' hata diya (Singular hona chahiye)
    }
    
    if request.method == 'POST':
        first = request.POST['first']
        last = request.POST['last']
        mymember.firstname = first
        mymember.lastname = last
        mymember.save()
        messages.success(request, "Details update ho gayi hain! ✅")
        return HttpResponseRedirect(reverse('index'))
        
    return HttpResponse(template.render(context, request))

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