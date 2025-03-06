"""Vista para manejo de acciones de inciencias de nomina"""

import json
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import  get_object_or_404, render
from django.views import generic
from django.http.response import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from worklife.models import VacationRequest,AbsenceRegistry
from worklife.models import WorkIncident,WorkTimePeriod,WorkTimeRecord
from django.http import JsonResponse
from django.template.loader import render_to_string

def index(request):
  return render(request, "worklife/index.html")


class WorkDurationView(LoginRequiredMixin, generic.TemplateView):
    """Vista para manejar el inicio de labores del trabajador"""
    template_name = 'worklife/workduration.html'

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            
            # Obtener el usuario correctamente
            user = self.request.user
            
            # Verificar si hay login para hoy
            user_has_login = WorkTimePeriod.objects.filter(
                user=user,
                date__date=timezone.now()
            ).exists()
            
            # Determinar estados basados en el último registro
            latest_record = WorkTimeRecord.objects.filter(
                user=user,
                datetime__date=timezone.now()
            ).order_by('-datetime').first()
            
            context.update({
                "user_has_login": user_has_login,
                "user_has_resumed": True if latest_record and latest_record.record_type == "0" else False,
                "user_has_pause": True if latest_record and latest_record.record_type == "2" else False,
                "user_has_ended": True if latest_record and latest_record.record_type == "1" else False
            })
            
            return context
    
    def post(self, request):
        success = False
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
       
        if request_json.get('state') == '2':
            current_period = WorkTimePeriod.objects.filter(
            user=self.request.user,
            date__date=timezone.now()
        ).first()
            WorkTimeRecord.objects.create(
            datetime=timezone.now(),
           period_id=current_period.id,
                    record_type="2",
            user_id=request.user.id,
          )
            success = True

        if request_json.get('state') == '3':
            current_period = WorkTimePeriod.objects.filter(
            user=self.request.user,
            date__date=timezone.now()
        ).first()
            WorkTimeRecord.objects.create(
            datetime=timezone.now(),
           period_id=current_period.id,
                    record_type="0",
            user_id=request.user.id,
          )
            success = True


        if request_json.get('state') == '1':
            current_period = WorkTimePeriod.objects.filter(
            user=self.request.user,
            date__date=timezone.now()
        ).first()
            WorkTimeRecord.objects.create(
            datetime=timezone.now(),
           period_id=current_period.id,
                    record_type="1",
            user_id=request.user.id,
          )
            success = True


        if request_json.get('state') == '4':
            current_period = WorkTimePeriod.objects.filter(
            user=self.request.user,
            date__date=timezone.now()
        ).first()
            
            latest_record = WorkTimeRecord.objects.filter(
                    user=self.request.user,
                    datetime__date=timezone.now()
                ).order_by('-datetime').first()
        
            if latest_record:
               latest_record.delete()
            success = True

        return JsonResponse({
            "success": success,
            "message": message
        })

   


class CalendarView(LoginRequiredMixin, generic.TemplateView):
    """Vista para manejar el inicio de labores del trabajador"""
    template_name = 'worklife/calendar.html'

    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Validar datos requeridos
            required_fields = ['type', 'description', 'start', 'end']
            if not all(field in data for field in required_fields):
                return JsonResponse({
                    'success': False,
                    'message': 'Faltan campos requeridos en la solicitud'
                }, status=400)

            # Crear incidente
            incident = WorkIncident.objects.create(
                user=request.user,
                incident_type=data['type'],
                comments=data['description'],
                incident_start=data['start'],
                incident_end=data['end']
            )

            # Crear solicitud de vacaciones
            vacation = VacationRequest.objects.create(
                incident=incident,
                user=request.user,
                vacation_start=data['start'],
                vacation_end=data['end'],
                detail=data['description']
            )

            return JsonResponse({
                'success': True,
                'message': 'Incidente guardado exitosamente'
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Formato JSON inválido'
            }, status=400)

        except KeyError as e:
            return JsonResponse({
                'success': False,
                'message': f'Campo requerido faltante: {str(e)}'
            }, status=400)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)

class IncidentsView(LoginRequiredMixin, generic.ListView):
    """Vista para Visualizar las incidencias que tiene el trabajador"""
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
            if incident.applied == None:
               class_name = 'pending-event'
            
            if incident.applied == False:
               class_name = 'no-accepted-event'
            
            if incident.applied == True:
               class_name = 'accepted-event'
            
            event = {
                'className': class_name,
                'id': incident.id,
                'title': incident.formatted_incident_type,
                'start': incident.incident_start.isoformat(),
                'end': incident.incident_end.isoformat(),
                'description': f"Incident #{incident.incident_type} {incident.comments}"
            }
            
            if incident.applied == None:
              event['status'] = "Requested"
            
            if incident.applied == False:
               event['status'] = "Not applied"
            
            if incident.applied == True:
               event['status'] = "Applied"
            
            events.append(event)
        return json.dumps(events)  
    


class AbsencesView(LoginRequiredMixin, generic.ListView):
            """Vista para Visualizar las Aunsencias de los colaboradores"""
            template_name = "worklife/absence.html"
            
            def get_queryset(self):
                return AbsenceRegistry.objects.select_related('incident', 'user').all()
            
            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context['calendar_events'] = self.get_calendar_events()
                return context
            
            def get_calendar_events(self):
                events = []
                for absence in self.get_queryset():
                    if absence.incident.incident_type == "3":
                            class_name = 'unjustified-absences'
                
                    if absence.incident.incident_type == "4":
                            class_name = 'justified-absences'
                
                    event = {
                        'className': class_name,
                        'id': absence.id,
                        'user': absence.user.get_full_name(),
                        'title': absence.incident.formatted_incident_type,
                        'start': absence.absence_start.isoformat(),
                        'end': absence.absence_end.isoformat(),
                        'description': f"Incident #{absence.incident.incident_type} {absence.detail}"
                    }

                    if absence.incident.applied == None:
                         event['status'] = "Requested"
            
                    if absence.incident.applied == False:
                         event['status'] = "Not applied"
                    
                    if absence.incident.applied== True:
                        event['status'] = "Applied"
            
        
                    
                    events.append(event)
                return json.dumps(events) 
    

class VacationsView(LoginRequiredMixin, generic.ListView):
            """Vista para Visualizar las vacacciones  de los colaboradores"""
            template_name = "worklife/vacations.html"
            
            def get_queryset(self):
                return WorkIncident.objects.all()
            
            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context['calendar_events'] = self.get_calendar_events()
                return context
            
            def get_calendar_events(self):
                events = []
                for incident in self.get_queryset():
                    if incident.applied == None:
                        class_name = 'pending-event'
                    
                    if incident.applied == False:
                        class_name = 'no-accepted-event'
                    
                    if incident.applied == True:
                         class_name = 'accepted-event'
                    
                    if incident.incident_type == "0":
                        event = {
                            'className': class_name,
                            'id': incident.id,
                            'user': incident.user.get_full_name(),
                            'username': incident.user.username,
                            'title': incident.formatted_incident_type,
                            'start': incident.incident_start.isoformat(),
                            'end': incident.incident_end.isoformat(),
                            'description': f"Incident #{incident.incident_type} {incident.comments}"
                        }

                    
                        
                        if incident.applied == None:
                            event['status'] = "Requested"
                        
                        if incident.applied == False:
                            event['status'] = "Not applied"
                        
                        if incident.applied == True:
                            event['status'] = "Applied"

                        events.append(event)
                return json.dumps(events) 




class CincidentsView(LoginRequiredMixin, generic.ListView):
            """Vista para Visualizar las  Incidencias de los colaboradores"""
            template_name = "worklife/cincidents.html"
            
            def get_queryset(self):
                return WorkIncident.objects.select_related('user').all()
            
            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context['calendar_events'] = self.get_calendar_events()
                return context
            
            def get_calendar_events(self):
                events = []
                for incident in self.get_queryset():
                    if incident.applied == None:
                        class_name = 'pending-event'
                    
                    if incident.applied == False:
                        class_name = 'no-accepted-event'
                    
                    if incident.applied == True:
                         class_name = 'accepted-event'
                    
                    if incident.incident_type != "0":
                        event = {
                            'className': class_name,
                            'id': incident.id,
                            'user': incident.user.get_full_name(),
                            'username': incident.user.username,
                            'title': incident.formatted_incident_type,
                            'start': incident.incident_start.isoformat(),
                            'end': incident.incident_end.isoformat(),
                            'description': f"Incident #{incident.incident_type} {incident.comments}"
                        }

                    
                        
                        if incident.applied == None:
                            event['status'] = "Requested"
                        
                        if incident.applied == False:
                            event['status'] = "Not applied"
                        
                        if incident.applied == True:
                            event['status'] = "Applied"

                        events.append(event)
                return json.dumps(events) 





class RequestView(LoginRequiredMixin, generic.ListView):
    """Vista para  Manejar las Solicitudes de Incidencias de los colaboradores"""
    template_name = "worklife/request.html"
    model = VacationRequest
    paginate_by = 3
    context_object_name = 'vacation_requests'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        page_size = int(self.request.GET.get('page_size', 3))
        vacation_requests = self.get_filtered_vacation_requests()
        
        paginator = Paginator(vacation_requests, page_size)
        page_number = self.request.GET.get('page', 1)
        try:
            page_obj = paginator.get_page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.get_page(1)
        except EmptyPage:
            page_obj = paginator.get_page(paginator.num_pages)
        
        context['vacation_requests'] = page_obj
        context['incidents'] = WorkIncident.objects.order_by('-incident_start').all()
        context['page_size'] = page_size
        
        # Verificar si la solicitud es Ajax comprobando el encabezado HTTP_X_REQUESTED_WITH
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Si es una solicitud Ajax, devolver solo el HTML de la lista
            return JsonResponse({
                'html': render_to_string('worklife/request_list.html', context),
                'page': page_obj.number,
                'total_pages': paginator.num_pages,
            })
        
        return context

    def get_filtered_vacation_requests(self):
        queryset = VacationRequest.objects.select_related('incident').order_by(
            F('approved').asc(nulls_first=True), '-incident__incident_start'
        )
        
        status = self.request.GET.get('status')
        if status == 'None':
            queryset = queryset.filter(approved=None)
        elif status == 'False':
            queryset = queryset.filter(approved=False)
        elif status == 'True':
            queryset = queryset.filter(approved=True)
        elif status == 'All':
            queryset = queryset.all()
        
        return queryset



            
def set_not(request, incident_id, vacationrequest_id):
        vacationrequest = get_object_or_404(VacationRequest, pk=vacationrequest_id)
        incident = get_object_or_404(WorkIncident, pk=incident_id)
        if request.method == 'POST':
            vacationrequest .approved = False
            vacationrequest.save()
            
            incident.applied = False
            incident.save()
            return HttpResponseRedirect(reverse("worklife:requestvi"))
        
        return HttpResponseRedirect(reverse("worklife:requestvi"))


def set_yes(request, iincident_id, vacationrequest_id):
        vacationrequest = get_object_or_404(VacationRequest, pk=vacationrequest_id)
        incident = get_object_or_404(WorkIncident, pk=iincident_id)
        if request.method == 'POST':  
            vacationrequest .approved = True
            vacationrequest.save()
       
            incident .applied = True
            incident.save()
            return HttpResponseRedirect(reverse("worklife:requestvi"))
        
        return HttpResponseRedirect(reverse("worklife:requestvi"))

def set_update(request):
    try:
        # Asegurarnos de que el contenido es JSON
        if not request.content_type.startswith('application/json'):
            return JsonResponse({
                'success': False,
                'message': 'El contenido debe ser JSON'
            }, status=400)
        
        data = json.loads(request.body)
        
        # Validación completa
        required_fields = ['id_v', 'description', 'start', 'end', 'approved']
        if not all(field in data for field in required_fields):
            return JsonResponse({
                'success': False,
                'message': 'Faltan campos requeridos en la solicitud'
            }, status=400)
        
        # Validación de tipos
        if not isinstance(data.get('approved'), bool):
            return JsonResponse({
                'success': False,
                'message': 'El campo "approved" debe ser booleano'
            }, status=400)
        
        vacation_request = get_object_or_404(VacationRequest, pk=data['id_v'])
        incident = get_object_or_404(WorkIncident, pk=vacation_request.incident_id)
        vacation_request.detail = data['description']
        vacation_request.vacation_start = data['start']
        vacation_request.vacation_end = data['end']
        vacation_request.approved = data['approved']


        incident.incident_type = data['type']
        incident.comments = data['description']
        incident.incident_start = data['start']
        incident.incident_end = data['end']
        incident.applied = data['approved']

        try:
            vacation_request.save()
            incident.save()
            return JsonResponse({
                'success': True,
                'message': 'Vacación actualizada exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Error al guardar la solicitud',
                'error': str(e)
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'El formato JSON es inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }, status=500)

@csrf_exempt
def verify_login_today(request):
    if request.user.is_authenticated:
        # Obtener el primer registro del día
        first_login = WorkTimePeriod.objects.filter(
            user=request.user,
            date__date=timezone.now().date()
        ).order_by('date').first()
        
        # Determinar estados basados en el último registro
        latest_record = WorkTimeRecord.objects.filter(
            user=request.user,
            datetime__date=timezone.now()
        ).order_by('-datetime').first()
        
        return JsonResponse({
            'has_login': True,
            'first_login_time': first_login.date.isoformat() if first_login else None,
            'user_has_pause': latest_record and latest_record.record_type == "2",
            'user_has_resumed': latest_record and latest_record.record_type == "0",
            'user_has_ended': latest_record and latest_record.record_type == "1"
        })
    return JsonResponse({
        'has_login': False,
        'error': 'No autenticado'
    })
            
 
@csrf_exempt
def get_workday_end(request):
    if request.user.is_authenticated:
        # Obtener el registro de fin de jornada
        end_record = WorkTimeRecord.objects.filter(
            user=request.user,
            datetime__date=timezone.now(),
            record_type="1"  # 1 representa el fin de la jornada
        ).order_by('-datetime').first()
        
        if end_record:
            return JsonResponse({
                'end_time': end_record.datetime.isoformat()
            })
        else:
            return JsonResponse({
                'error': 'No se encontró el registro de fin de jornada'
            })
    return JsonResponse({
        'error': 'No autenticado'
    })



class CollaboratorView(LoginRequiredMixin, generic.ListView):
            """Vista para  Visualizar Los periodos de Trabajo de los Colaboradores."""
            template_name = "worklife/collaborator.html"
            
            def get_queryset(self):
                return WorkTimeRecord.objects.select_related('period').all()
            
            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context['calendar_events'] = self.get_calendar_events()
                return context
            
            def get_calendar_events(self):
                events = []
                for worktimerecord in self.get_queryset():
                    # Filtrar solo registros con record_type=0
                    if worktimerecord.record_type != "0":
                        continue
                        
                    # Determinar estados basados en el último registro
                    latest_record = WorkTimeRecord.objects.filter(
                        user=worktimerecord.user,
                        record_type="1",
                        datetime__date=worktimerecord.period.date
                    ).order_by('-datetime').first()
                    
                    event = {
                        'className': 'collaborator',
                        'user': worktimerecord.user.get_full_name(),
                        'title': f"#{worktimerecord.id} {worktimerecord.user.username}",
                        'start': worktimerecord.period.date.isoformat()
                    }
                    
                    # Solo agregar el campo 'end' si existe un registro válido
                    if latest_record is not None:
                        event['end'] = latest_record.datetime.isoformat()
                        event['description'] = "Jornada finalizada"

                    if latest_record is  None:
                        event['description'] = "Jornada en Proceso"


                    events.append(event)
                
                return json.dumps(events)
