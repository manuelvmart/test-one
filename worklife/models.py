from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save,pre_save
# Create your models here.
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
from django.dispatch import receiver

class WorkTimePeriod(models.Model):
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
                incident = models.ForeignKey(WorkIncident, on_delete=models.CASCADE, null=True, blank=True)
                user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
                vacation_start = models.DateTimeField("VacationStartTime")
                vacation_end = models.DateTimeField("VacationEndTime")
                approved = models.BooleanField(null=True)
                detail = models.CharField(max_length=200)

@receiver(post_save, sender=VacationRequest)
def save_post(sender, instance, **kwargs):
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
                incident = models.ForeignKey(WorkIncident, on_delete=models.CASCADE, null=True, blank=True)
                user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
                absence_start =  models.DateTimeField("AbsenceStartTime")
                absence_end  =  models.DateTimeField("AbsenceStartTime")
                absence_type = models.CharField (choices=(("0", "Unjustified absences"), ("1", "Justified absences"))
                                                 ,  max_length=1,null=True)
                detail =  models.CharField(max_length=200)