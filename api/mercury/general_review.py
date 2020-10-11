import pickle
import os
from django.db.models import Sum
from ..models import ATM, Bank, AtmCrowdedPlace, PeopleFlow, Polygon, CrowdedPlace
import json
from haversine import haversine
from shapely import wkt, geometry
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
        self.crowded_places = CrowdedPlace.objects.all()
        self.atm_crowded_places = AtmCrowdedPlace.objects.all()
        self.bank = Bank.objects.get(name=bank_name)
        self.polygons = Polygon.objects.all()
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

        polygons = {polygon.square_id: polygon.wkt_geo for polygon in self.polygons}
        work_list = {}
        feature = 0.35

        for polygon in self.data['proba_values']:
            # is_have_nearest_atm = False
            # poly_wkt = wkt.loads(polygons[polygon])
            # x, y = poly_wkt.centroid.coords.xy
            #
            # for atm in self.atm:
            #     if atm.bank.name == 'Газпромбанк':
            #         distance = haversine((atm.lon, atm.lat), (x[0], y[0]))
            #         if distance <= .8:
            #             is_have_nearest_atm = True
            #             break
            #
            # if is_have_nearest_atm:
            #     continue

            if self.data['proba_values'][polygon] >= feature:
                work_list[polygon] = self.data['proba_values'][polygon]

        for polygon in work_list:
            polygon_list = [wkt.loads(polygons[polygon])]

            for i in range(-5, 5):
                second_polygon = str(int(polygon) + i)

                if second_polygon in work_list.keys():
                    polygon_list.append(wkt.loads(polygons[second_polygon]))

            if len(polygon_list) < 2:
                continue

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

            obj = get_feature_obj(polygon, 0, [bounds])
            res.append(obj)

        print(len(res))

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
    
    def get_polygon_flow_scores(self):
        scores = {}
        max_val = -100

        for time in self.data['people_flow']:
            for polygon in self.data['people_flow'][time]:

                if polygon not in scores.keys():
                    scores[polygon] = {
                        'sum': 0,
                        'count': 0
                    }

                scores[polygon]['sum'] += self.data['people_flow'][time][polygon]['sum']
                scores[polygon]['count'] += 1

                if scores[polygon]['sum'] > max_val:
                    max_val = scores[polygon]['sum']

        day_scores = {polygon: scores[polygon]['sum'] / scores[polygon]['count'] for polygon in scores}
        max_val = max(day_scores.values())
        absolute_scores = {polygon: day_scores[polygon] / max_val for polygon in day_scores}

        return absolute_scores

    def get_polygon_place_scores(self):
        polygon_places = {}

        for place in self.crowded_places:
            square_id = place.square_id.square_id

            if square_id not in polygon_places:
                polygon_places[square_id] = {}

            polygon_places[square_id][place.type] = polygon_places[square_id][place.type] + 1 if place.type in polygon_places[square_id].keys() else 1

        return polygon_places

    def construct_predict_polygons_object(self):
        obj = {'proba_values': {}}

        polygon_ignore_list = [673420]

        categories_weights = {
            'people_flow': 0.8,
            'public_transport_stop': 0.6,
            'shopping_mall': 0.5,
            'gas_station': 0.4,
        }

        polygon_place_scores = self.get_polygon_place_scores()
        polygon_flow_scores = self.get_polygon_flow_scores()

        for polygon in self.polygons:

            if polygon.id in polygon_ignore_list:
                continue

            place_scores = polygon_place_scores[polygon.square_id] if polygon.square_id in polygon_place_scores else {}
            flow_score = polygon_flow_scores[polygon.square_id] if polygon.square_id in polygon_flow_scores else 0

            func = flow_score * categories_weights['people_flow']
            power = 3

            for item in place_scores:
                value = categories_weights[item]**power
                func += place_scores[item]*value
                power += 1

            obj['proba_values'][polygon.square_id] = func

        max_val = max(obj['proba_values'].values())
        obj['proba_values'] = {polygon: obj['proba_values'][polygon] / max_val for polygon in obj['proba_values']}

        return obj
