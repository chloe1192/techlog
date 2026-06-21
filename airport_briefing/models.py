from techlog.models import Airport, Operator
from django.db import models

class AirportCategoryChoices(models.IntegerChoices):
    A = 0, "Category A"
    B = 1, "Category B"
    C = 2, "Category C"
    D = 3, "Category D"

class NadpChoices(models.IntegerChoices):
    NADP1 = 0, "NADP 1"
    NADP2 = 1, "NADP 1"

class AirportBriefing(models.Model):
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    category = models.IntegerField(choices=AirportCategoryChoices)
    general_text = models.TextField(blank=True, null=True)
    departure_text = models.TextField(blank=True, null=True)
    arrival_text = models.TextField(blank=True, null=True)
    thr_red_alt = models.IntegerField(null=True, blank=True)
    acc_alt = models.IntegerField(null=True, blank=True)
    eo_acc_alt = models.IntegerField(null=True, blank=True)
    nadp = models.IntegerField(choices=NadpChoices, blank=True, null=True)

class Runway(models.Model):
    name = models.CharField(max_length=3)
    heading = models.IntegerField()
    app_avail = models.CharField(max_length=6)
    toda = models.IntegerField()
    tora = models.IntegerField()
    asda = models.IntegerField()
    lda = models.IntegerField()
    altitude = models.IntegerField()

class EoSid(models.Model):
    runway = models.ForeignKey(Runway, on_delete=models.CASCADE)
    text = models.TextField()

class LandingDistances(models.Model):
    runway = models.ForeignKey(Runway, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    distance = models.IntegerField()