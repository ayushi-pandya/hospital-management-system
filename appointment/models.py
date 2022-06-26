from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import models
from users.models import CustomUser, Staff


def date_validation(date):
    """
    function for date validation of appointment.
    """
    today = date.today()
    if date < today:
        raise ValidationError("The date cannot be in the past! Please select valid date.")
    return date


def timeslot_validation(time):
    """
    function for date validation of appointment.
    """
    today = datetime.now()
    if time < today:
        raise ValidationError("The time cannot be in the past! Please select valid time.")
    return time


class Appointments(models.Model):
    """
    This class is for creating table of appointment.
    """
    TIMESLOT_LIST = (
        ('09:00 – 09:30', '09:00 – 09:30'),
        ('10:00 – 10:30', '10:00 – 10:30'),
        ('11:00 – 11:30', '11:00 – 11:30'),
        ('12:00 – 12:30', '12:00 – 12:30'),
        ('13:00 – 13:30', '13:00 – 13:30'),
        ('14:00 – 14:30', '14:00 – 14:30'),
        ('15:00 – 15:30', '15:00 – 15:30'),
        ('16:00 – 16:30', '16:00 – 16:30'),
        ('17:00 – 17:30', '17:00 – 17:30'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField(validators=[date_validation],
                            help_text="Use that Format:YYYY-MM-DD...For example: 2022-6-26")
    timeslot = models.CharField(max_length=100, choices=TIMESLOT_LIST)
    disease = models.CharField(max_length=300)

    def __str__(self):
        return f"Patient: {self.user} | Time: {self.timeslot}"
