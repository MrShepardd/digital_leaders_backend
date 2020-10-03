from django.db import models


class Bank(models.Model):
    name = models.CharField(max_length=200)


class CrowdedPlace(models.Model):
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    gis_id = models.CharField(max_length=200)
    lat = models.FloatField(default=-1.0)
    lon = models.FloatField(default=-1.0)


class ATM(models.Model):
    gis_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, default=0)
    address = models.CharField(max_length=200)
    lat = models.FloatField(default=-1.0)
    lon = models.FloatField(default=-1.0)
    schedule = models.TextField(default="")


class AtmCrowdedPlace(models.Model):
    id_atm = models.ForeignKey(ATM, on_delete=models.CASCADE, default=0)
    id_place = models.ForeignKey(CrowdedPlace, on_delete=models.CASCADE, default=0)
    distance = models.FloatField(default=0.0)
    measure = models.CharField(max_length=200)
    multi_line_string = models.TextField(default="")


class District(models.Model):
    name = models.CharField(max_length=200)
    gis_id = models.CharField(max_length=200)
    population = models.IntegerField(default=0)
    address = models.CharField(max_length=200)
    lat = models.FloatField(default=-1.0)
    lon = models.FloatField(default=-1.0)
    geometry = models.TextField(default="")
