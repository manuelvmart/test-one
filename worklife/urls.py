from django.urls import path

from . import views
app_name = "worklife"
urlpatterns = [
    path("", views.index, name="index"),
   path('workduration/', views.workduration, name='workduration')
]