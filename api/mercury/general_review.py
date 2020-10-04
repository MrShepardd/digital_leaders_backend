import json
import pickle
import os
import datetime
import numpy as N
from django.db.models import Sum
from ..models import ATM, Bank, AtmCrowdedPlace, PeopleFlow, Polygon, CrowdedPlace
import json
from haversine import haversine
from shapely import wkt
from shapely import geometry
from shapely.ops import cascaded_union


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
        obj.update(self.construct_predict_polygons_object())
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, 'wb') as f:
            pickle.dump(obj, f)

    def get_cluster_polygons(self):

        res = []

        polygons = {polygon.square_id: polygon.wkt_geo for polygon in Polygon.objects.all()}
        work_list = {}
        feature = 0.1

        for polygon in self.data['proba_values']:
            is_have_nearest_atm = False
            poly_wkt = wkt.loads(polygons[polygon])
            x, y = poly_wkt.centroid.coords.xy

            for atm in self.atm:
                if atm.bank.name == 'Газпромбанк':
                    distance = haversine((atm.lon, atm.lat), (x[0], y[0]))
                    if distance <= .8:
                        is_have_nearest_atm = True
                        break

            if is_have_nearest_atm:
                continue

            if self.data['proba_values'][polygon] >= feature:
                work_list[polygon] = self.data['proba_values'][polygon]

        for polygon in work_list:
            polygon_list = [wkt.loads(polygons[polygon])]

            for i in range(-10, 10):
                second_polygon = str(int(polygon) + i)

                if second_polygon in work_list.keys():
                    polygon_list.append(wkt.loads(polygons[second_polygon]))

            u = cascaded_union(polygon_list)
            bounds = []

            if u.type == "MultiPolygon" and u.is_valid and len(polygons) > 1:
                for item in u:
                    gg_json = list(item.exterior.coords)
                    for gg in gg_json:
                        bounds.append([gg[0], gg[1]])
            elif u.is_valid:
                gg_json = list(u.exterior.coords)
                for gg in gg_json:
                    bounds.append([gg[0], gg[1]])

            # res.append(bounds)

            obj = get_feature_obj(polygon, 0, [bounds])
            res.append(obj)

        return res

    def get_atm_location(self):
        res = []

        for i in range(len(self.atm)):

            # if self.atm[i].bank != self.bank:
            #     continue

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
        obj = {'proba_values': {}}

        polygons = {polygon.square_id: polygon.wkt_geo for polygon in Polygon.objects.all()}

        polygon_places = {}
        for place in CrowdedPlace.objects.all():
            square_id = place.square_id.square_id
            if square_id not in polygon_places:
                polygon_places[square_id] = []

            polygon_places[square_id].append(place)

        max_values = {}
        categories_weights = {
            'people_flow': 0.8,
            'bus_stop': 0.6
        }

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
                scores[time][polygon] = self.data['people_flow'][time][polygon]['sum'] / max_value * categories_weights['people_flow']

        res = {}

        for time in scores:
            for polygon in scores[time]:

                if polygon not in res:
                    res[polygon] = {
                        'people_flow_sum': 0,
                        'people_flow_count': 0,
                        'people_flow_value': 0.0,
                        'bus_stop_sum': 0,
                        'bus_stop_count': 0,
                        'bus_stop_value': 0.0,
                        'total': 0.0
                    }

                res[polygon]['people_flow_sum'] += scores[time][polygon]
                res[polygon]['people_flow_count'] += 1

        for polygon in res:
            places = polygon_places[polygon] if polygon in polygon_places.keys() else []

            for place in places:
                weight = categories_weights[place.type]
                res[polygon]['bus_stop_sum'] += weight
                res[polygon]['bus_stop_count'] += 1

        for polygon in res:
            res[polygon]['people_flow_value'] = res[polygon]['people_flow_sum'] / res[polygon]['people_flow_count'] if res[polygon]['people_flow_count'] != 0 else 0.0
            res[polygon]['bus_stop_value'] = res[polygon]['bus_stop_sum'] / res[polygon]['bus_stop_count'] if res[polygon]['bus_stop_count'] != 0 else 0.0

            res[polygon]['total'] = (res[polygon]['people_flow_value'] + res[polygon]['bus_stop_value']) / 2
            obj['proba_values'][polygon] = res[polygon]['total']

        return obj
