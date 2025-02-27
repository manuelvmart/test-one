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
      path('collaborators/', views.CollaboratorView.as_view(), name='collaborators'),
      #path('absences/', views.AbsencesView.as_view(), name='absences'),
    path('requestvi/', views.RequestView.as_view(), name='requestvi'),
        path('<int:incident_id>/<int:vacationrequest_id>/set_not/', views.set_not, name='set_not'),
            path('<int:iincident_id>/<int:vacationrequest_id>/set_yes/', views.set_yes, name='set_yes'),
            path('verify-login/', views.verify_login_today, name='verify-login'),
             path('worklife/workduration/end/', views.get_workday_end, name='end-workday'),
]