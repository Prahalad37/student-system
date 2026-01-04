from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render
from .models import Member, StudyMaterial  # Dono models import hone chahiye

def index(request):
  mymembers = Member.objects.all().values()
  template = loader.get_template('index.html')
  return HttpResponse(template.render({'mymembers': mymembers, 'request': request}, request))

def add(request):
  template = loader.get_template('add.html')
  return HttpResponse(template.render({}, request))

def addrecord(request):
  x = request.POST['first']
  y = request.POST['last']
  member = Member(firstname=x, lastname=y)
  member.save()
  return HttpResponseRedirect(reverse('index'))

def delete(request, id):
  member = Member.objects.get(id=id)
  member.delete()
  return HttpResponseRedirect(reverse('index'))

def update(request, id):
  mymember = Member.objects.get(id=id)
  template = loader.get_template('update.html')
  context = {
    'mymember': mymymember,
  }
  return HttpResponse(template.render(context, request))

def updaterecord(request, id):
  first = request.POST['first']
  last = request.POST['last']
  member = Member.objects.get(id=id)
  member.firstname = first
  member.lastname = last
  member.save()
  return HttpResponseRedirect(reverse('index'))

# --- NEW LIBRARY VIEW ---
def library(request):
    # Saare materials lao, latest pehle
    materials = StudyMaterial.objects.all().order_by('-created_at')
    return render(request, 'library.html', {'materials': materials})