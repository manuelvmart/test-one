"""Vista para manejo de acciones de inciencias de nomina"""
import json
from django.utils import timezone
from django.shortcuts import render
from django.views import generic
from django.http.response import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from worklife.models import WorkIncident
from worklife.models import WorkTimePeriod
from worklife.models import WorkTimeRecord


def index(request):
  return render(request, "worklife/index.html")


class WorkDurationView(LoginRequiredMixin, generic.TemplateView):
    """Vista para manejar el inicio de labores del trabajador"""
    template_name = 'worklife/workduration.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_has_login = WorkTimePeriod.objects.filter(
            user=self.request.user,
            date__date=timezone.now()
        ).exists()

        context.update({
            "user_has_login": user_has_login,
        })

        return context
    
    def post(self, request):
        succes = False
        message = "Hubo un error en el procesamiento."
        request_json = json.loads(request.body)
        # states.STARTING_WORK_DAY
        if request_json.get('state') == '0':
            if not WorkTimePeriod.objects.filter(
                user=self.request.user,
                date__date=timezone.now()
            ).exists():
                worktimeperiod = WorkTimePeriod.init_work_day(
                    request.user,
                    timezone.now()
                )
                if worktimeperiod:
                    success = True
                    message = "Inicio de sesión completado"


        return JsonResponse({
            "success": success,
            "message": message
        })

   


@login_required
def calendar(request):
    return render(request,"worklife/calendar.html")


class IncidentsView(LoginRequiredMixin, generic.ListView):
    template_name = "worklife/incidents.html"
    
    def get_queryset(self):
        return WorkIncident.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calendar_events'] = self.get_calendar_events()
        return context
    
    def get_calendar_events(self):
        events = []
        for incident in self.get_queryset():
            event = {
                'id': incident.id,
                'title': incident.incident_type,
                'start': incident.incident_start.isoformat(),
                'end': incident.incident_end.isoformat(),
                'description': f"Incident #{incident.incident_type} {incident.comments}"
            }

            if incident.incident_type == "2":
               event['title'] = " (Delay)"
            
            if incident.incident_type == "0":
               event['title'] = "(Vacations)"
            
            if incident.incident_type == "3":
               event['title'] = "(Unjustified absences)"
            

            if incident.incident_type == "4":
               event['title'] = " (Justified absences)"

            if incident.incident_type == "5":
               event['title'] = "(Maternity leave)"

            
            if incident.incident_type == "6":
               event['title'] = "(Work Incapacity)"
            
            events.append(event)
        return json.dumps(events)  

@login_required
def requestvi(request):
    return render(request,"worklife/request.html")