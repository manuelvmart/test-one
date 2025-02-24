from django.urls import path

from . import views
app_name = "worklife"
urlpatterns = [
    path("", views.index, name="index"),
   path('workduration/', views.WorkDurationView.as_view(), name='workduration'),
   path('calendar/', views.CalendarView.as_view(), name='calendar'),
   path('incidents/', views.IncidentsView.as_view(), name='incidents'),
   path('cincidents/', views.CincidentsView.as_view(), name='cincidents'),
   path('vacations/', views.VacationsView.as_view(), name='vacations'),
      #path('absences/', views.AbsencesView.as_view(), name='absences'),
    path('requestvi/', views.RequestView.as_view(), name='requestvi'),
        path('<int:vacationrequest_id>/set_not/', views.set_not, name='set_not'),
]