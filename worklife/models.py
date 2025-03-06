import logging
from django.db import models
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

#nuevo Log para imprimir en terminal
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class WorkTimePeriod(models.Model):
    """Modelo utilizado para almacenar los datos De el Periodo de Trabajo de un colaborador."""
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    date =  models.DateTimeField("WorkTime", auto_now_add=True)

    @staticmethod
    def init_work_day(user, _date):
        worktimeperiod = WorkTimePeriod.objects.create(
            user=user,
            date=_date
        )
        # states.INIT_...
        _ = WorkTimeRecord.objects.create(
            user=user,
            period=worktimeperiod,
            datetime=_date,
            record_type="0"
        )
        return worktimeperiod
     


class WorkTimeRecord(models.Model):
    """Modelo utilizado para almacenar los datos De inicio de trabajo , descanso y fin de jornada. de Trabajo de un colaborador."""
    user = user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    period = models.ForeignKey(WorkTimePeriod, on_delete=models.CASCADE)
    datetime = models.DateTimeField("Time")
    record_type = models.CharField(
        choices=(
            ("0", "Start of working day"),
            ("1", "End of working day"),
            ("2", "Break")
        ),
        max_length=1
    )
                
class WorkIncident(models.Model):
                """Modelo utilizado para almacenar los datos De  las incidencias de un colaborador."""
                user  = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
                incident_type = models.CharField (choices=(("0", "Vacations"), ("2", "Delay"), ("3", "Unjustified absences"), ("4", "Justified absences"), ("5", "Maternity leave"), 
                                                           ("6", "Work Incapacity")),  max_length=1)
                comments =  models.CharField(max_length=200)
                incident_start =models.DateTimeField("IncidentStartTime")
                incident_end = models.DateTimeField("IncidentEndTime")
                applied = models.BooleanField(null=True)


                @property
                def formatted_incident_type(self):
                    INCIDENT_TYPES = {
                        "2": "Delay",
                        "0": "Vacations",
                        "3": "Unjustified absences",
                        "4": "Justified absences",
                        "5": "Maternity leave",
                        "6": "Work Incapacity"
                    }
                    base_type = self.incident_type
                    return f"{base_type} ({INCIDENT_TYPES.get(base_type, '')})"

class VacationRequest(models.Model):
                """Modelo utilizado para almacenar los datos De   las solicitudes de los colaboradores."""
                incident = models.ForeignKey(WorkIncident, on_delete=models.CASCADE, null=True, blank=True)
                user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
                vacation_start = models.DateTimeField("VacationStartTime")
                vacation_end = models.DateTimeField("VacationEndTime")
                approved = models.BooleanField(null=True)
                detail = models.CharField(max_length=200)

@receiver(post_save, sender=VacationRequest)
def save_post(sender, instance, **kwargs):
    """Signals que se disparan despues de que un incidente corresponda  a una ausencia."""
    if hasattr(instance, 'incident') and instance.incident.incident_type == "3"  and instance.approved==True:
        logger.info("Tipo NO Justificado")
        AbsenceRegistry.objects.create(
                absence_start=instance.vacation_start,
                absence_end=instance.vacation_end,
                detail=instance.detail,
                incident_id=instance.incident.id,
                user_id=instance.user_id,
                absence_type=instance.incident.incident_type,
            )
    if hasattr(instance, 'incident') and instance.incident.incident_type == "4" and instance.approved==True:
        logger.info("Tipo Justificado")
        AbsenceRegistry.objects.create(
                absence_start=instance.vacation_start,
                absence_end=instance.vacation_end,
                detail=instance.detail,
                incident_id=instance.incident.id,
                user_id=instance.user_id,
                absence_type=instance.incident.incident_type,
            )




class AbsenceRegistry(models.Model):
                """Modelo utilizado para almacenar los datos De   las  ausencias  los colaboradores."""
                incident = models.ForeignKey(WorkIncident, on_delete=models.CASCADE, null=True, blank=True)
                user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
                absence_start =  models.DateTimeField("AbsenceStartTime")
                absence_end  =  models.DateTimeField("AbsenceStartTime")
                absence_type = models.CharField (choices=(("0", "Unjustified absences"), ("1", "Justified absences"))
                                                 ,  max_length=1,null=True)
                detail =  models.CharField(max_length=200)