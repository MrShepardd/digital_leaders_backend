import json
import pickle
import os
import datetime
import numpy as N
from django.db.models import Sum
from ..models import ATM, Bank, AtmCrowdedPlace, PeopleFlow, Polygon
import json
from haversine import haversine
from shapely import wkt


def get_format_distance(distance, measure):

    if measure == 'км' and distance < 1:
        return str(distance * 1000) + 'м'
    else:
        return str(distance) + 'км'


def get_feature_obj(square_id, sum, coords):
    return {
        'type': "Feature",
        'properties': {
            'square_id': square_id,
            'sum': sum,
        },
        'geometry': {
            'type': "Polygon",
            'coordinates': coords,
        },
    }


class GeneralReview:
    def __init__(self, bank_name='Газпромбанк', prefix=''):
        self.prefix = prefix
        self.filename = self.prefix + 'data/pre_calculation/' + bank_name + '/general_metrics.pckl'
        self.data = self.load_pre_calculation()
        self.atm = ATM.objects.all()
        self.atm_crowded_places = AtmCrowdedPlace.objects.all()
        self.bank = Bank.objects.get(name=bank_name)
        self.people_flow = PeopleFlow.objects.filter(date='2019-11-01').filter(
            abnt_cnt__gt=0).filter(age_min__gt=18).values('square_id', 'time').annotate(sum=Sum('abnt_cnt'))

    def load_pre_calculation(self):
        if os.path.isfile(self.filename):
            with open(self.filename, 'rb') as f:
                return pickle.load(f)
        else:
            return {}

    def make_precalculation(self):
        obj = self.construct_people_flow_object()
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, 'wb') as f:
            pickle.dump(obj, f)

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

    def get_people_flow(self):
        res = {}

        for time in self.data['people_flow']:

            if time not in res:
                res[time] = []

            for item in self.data['people_flow'][time]:
                sum = self.data['people_flow'][time][item]['sum']
                wkt = self.data['people_flow'][time][item]['wkt']

                coords = [[float(cd) for cd in coord.strip().split(' ')] for coord in wkt[10:-2].split(',')]

                if sum > 10:
                    obj = get_feature_obj(item, sum, [coords])
                    res[time].append(obj)

        with open("flow_data.json", "w", encoding="utf-8") as file:
            json.dump(res, file)

        return res

    def construct_people_flow_object(self):
        obj = {'people_flow': {}}

        polygons = {polygon.id: {'square_id': polygon.square_id, 'wkt': polygon.wkt_geo} for polygon in Polygon.objects.all()}

        for item in self.people_flow:
            time = item['time'].strftime("%H:%M:%S")
            polygon = polygons[item['square_id']]
            square_id = polygon['square_id']

            if time not in obj['people_flow']:
                obj['people_flow'][time] = {}

            if square_id not in obj['people_flow'][time]:
                obj['people_flow'][time][square_id] = {
                    'sum': 0,
                    'wkt': polygon['wkt']
                }

            obj['people_flow'][time][square_id]['sum'] += item['sum']

        return obj

    def construct_predict_polygons_object(self):
        obj = {}

        max_values = {}
        weight = 0.4

        for time in self.data['people_flow']:
            max_value = -100

            for polygon in self.data['people_flow'][time]:
                if self.data['people_flow'][time][polygon]['sum'] > max_value:
                    max_value = self.data['people_flow'][time][polygon]['sum']
            max_values[time] = max_value

        scores = {}

        for time in self.data['people_flow']:
            max_value = max_values[time]

            if time not in scores:
                scores[time] = {}

            for polygon in self.data['people_flow'][time]:
                scores[time][polygon] = self.data['people_flow'][time][polygon]['sum'] / max_value * weight

        res = {}

        ind = 1

        for time in scores:
            ind = 1
            for polygon in scores[time]:
                ind += 1
                res[polygon] = res[polygon] + scores[time][polygon] if polygon in res else scores[time][polygon]

        for polygon in res:
            res[polygon] /= ind

        print(res)

        return obj
