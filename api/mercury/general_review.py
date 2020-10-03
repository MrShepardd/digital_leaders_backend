import json
import pickle
import os
import datetime
import numpy as N
from django.db.models import Count
from ..models import ATM, Bank, AtmCrowdedPlace


def get_format_distance(distance, measure):

    if measure == 'км' and distance < 1:
        return str(distance * 1000) + 'м'
    else:
        return str(distance) + 'км'


class GeneralReview:
    def __init__(self, bank_name='Газпромбанк', prefix=''):
        self.atm = ATM.objects.all()
        self.atm_crowded_places = AtmCrowdedPlace.objects.all()
        self.bank = Bank.objects.get(name=bank_name)

    def get_atm_location(self):
        res = []

        for i in range(len(self.atm)):

            if self.atm[i].bank != self.bank:
                continue

            obj = {
                'id': i,
                'latitude': self.atm[i].lat,
                'longitude': self.atm[i].lon,
                'name': self.atm[i].name,
            }

            res.append(obj)

        return res

    def get_crowded_places(self):
        res = []

        for i in range(len(self.atm_crowded_places)):

            place = self.atm_crowded_places[i].id_place

            obj = {
                'id': i,
                'latitude': place.lat,
                'longitude': place.lon,
                'name': place.name,
                'distance': get_format_distance(self.atm_crowded_places[i].distance, self.atm_crowded_places[i].measure)
            }

            res.append(obj)

        return res

    def get_path_crowded_places(self):
        res = []

        for i in range(len(self.atm_crowded_places)):

            path = json.loads(self.atm_crowded_places[i].multi_line_string)

            obj = {
                'level': 1,
                'path': path,
                'distance': get_format_distance(self.atm_crowded_places[i].distance, self.atm_crowded_places[i].measure)
            }

            res.append(obj)

        return res
