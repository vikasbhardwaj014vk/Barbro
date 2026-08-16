from django.db import models
from barber.models import Barber
from django.contrib.auth.models import User

class Appointment(models.Model):

    customer=models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    barber=models.ForeignKey(
        Barber,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    date=models.DateField()

    time=models.TimeField()

    service=models.CharField(max_length=100)

    status=models.CharField(
        max_length=20,
        choices=[
            ("Pending","Pending"),
            ("Accepted","Accepted"),
            ("Rejected","Rejected"),
            ("Completed","Completed"),
            ("Cancelled","Cancelled"),
        ],
        default="Pending"
    )

class HomeService(models.Model):

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    barber = models.ForeignKey(
        Barber,
        on_delete=models.CASCADE
    )

    service = models.CharField(max_length=50)

    date = models.DateField()

    time = models.TimeField()

    address = models.TextField()

    latitude = models.FloatField()

    longitude = models.FloatField()

    notes = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)