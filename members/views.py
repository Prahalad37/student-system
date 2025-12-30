from django.shortcuts import render
from django.contrib import messages
from django.db.models import Q
from .models import Member
from django.http import HttpResponseRedirect
from django.urls import reverse

def add(request):
  if request.method == 'POST':
    messages.success(request, "Student successfully add ho gaya! 🎉")
    return HttpResponseRedirect(reverse('index'))
    # User ne form bhar ke submit kiya hai
    first = request.POST['firstname']
    last = request.POST['lastname']
    
    # Database mein naya member banaya
    member = Member(firstname=first, lastname=last)
    member.save()
    
    # Wapas list wale page par bhej diya
    return HttpResponseRedirect(reverse('index'))
    
  else:
    # User ko bas khali form dikhao
    return render(request, 'add.html')

# 1. Index View (List dikhane ke liye)
def index(request):
    # 1. User ne search box mein kya likha? Wo nikala
    query = request.GET.get('q') 
    
    if query:
        # 2. Agar kuch search kiya hai, toh filter lagao
        # icontains = Case insensitive search (matlab 'Anil', 'anil' sab chalega)
        mymembers = Member.objects.filter(
            Q(firstname__icontains=query) | Q(lastname__icontains=query)
        )
    else:
        # 3. Agar kuch search nahi kiya, toh saare members dikhao (Purana tareeka)
        mymembers = Member.objects.all()
    
    context = {
        'mymembers': mymembers,
    }
    return render(request, 'index.html', context)

# 2. Details View (Profile dikhane ke liye)
def details(request, id):
    mymember = Member.objects.get(id=id)
    context = {
        'mymember': mymember,
    }
    return render(request, 'details.html', context)
def delete(request, id):
  # Member ko dhundo
  member = Member.objects.get(id=id)
  # Delete karo
  member.delete()
  # Wapas home page par jao
  messages.success(request, "Student delete kar diya gaya. 🗑️")
  return HttpResponseRedirect(reverse('index'))

def update(request, id):
  # ... (purana code) ...
  if request.method == 'POST':
    # ... (data save karne ke baad) ...
    mymember.save()
    
    # Ye nayi line add karein 👇
    messages.success(request, "Details update ho gayi hain! ✅")
    return HttpResponseRedirect(reverse('index'))
  
  if request.method == 'POST':
    # Naya data form se nikala
    first = request.POST['firstname']
    last = request.POST['lastname']
    
    # Member ka data change kiya
    mymember.firstname = first
    mymember.lastname = last
    mymember.save()
    
    # Wapas list par bhej diya
    return HttpResponseRedirect(reverse('index'))
    
  else:
    # Form dikhaya (purane data ke saath)
    context = {
      'mymember': mymember,
    }
    return render(request, 'update.html', context)