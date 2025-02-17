
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic.base import TemplateView
# Create your views here.
def index(request):
  return render(request, "worklife/index.html")

def workduration(request):
    return render(request,"worklife/workduration.html")

def calendar(request):
    return render(request,"worklife/calendar.html")

def incidents(request):
    return render(request,"worklife/incidents.html")

def requestvi(request):
    return render(request,"worklife/request.html")