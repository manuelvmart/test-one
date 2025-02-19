from django.urls import path

from . import views
app_name = "worklife"
urlpatterns = [
    path("", views.index, name="index"),
   path('workduration/', views.WorkDurationView.as_view(), name='workduration'),
   path('calendar/', views.CalendarView.as_view(), name='calendar'),
   path('incidents/', views.IncidentsView.as_view(), name='incidents'),
    path('requestvi/', views.requestvi, name='requestvi')
]