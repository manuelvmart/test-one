
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
# Create your views here.
def index(request):
  return render(request, "worklife/index.html")

@login_required
def workduration(request):
    return render(request,"worklife/workduration.html")


@login_required
def calendar(request):
    return render(request,"worklife/calendar.html")


@login_required
def incidents(request):
    return render(request,"worklife/incidents.html")


@login_required
def requestvi(request):
    return render(request,"worklife/request.html")