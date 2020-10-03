from ..models import CrowdedPlace, AtmCrowdedPlace, ATM
import pickle


def construct_atm_crowded_place(id_atm, id_place, multi_line_string, distance, measure):
    return AtmCrowdedPlace(
        id_atm=id_atm,
        id_place=id_place,
        multi_line_string=multi_line_string,
        distance=distance,
        measure=measure
    )


class AtmCrowdedPlaceFiller:
    def __init__(self, path='data/stops.xlsx', prefix=''):
        with open(prefix + 'data/atm_crowded_place.dictionary', 'rb') as file:
            self.crowded_places = pickle.load(file)

    def refill(self):
        AtmCrowdedPlace.objects.all().delete()

        rows = []
        for item in self.crowded_places:
            # if i % 100 == 0:
            #     print(i)

            atm = ATM.objects.get(gis_id=item)

            for place in self.crowded_places[item]:
                cwd_place = CrowdedPlace.objects.get(gis_id=place['gis_id'])
                rows.append(construct_atm_crowded_place(atm, cwd_place, place['multi_line_string'], place['distance'], place['measure']))

        AtmCrowdedPlace.objects.bulk_create(rows)

        print('atm crowded places refilled')
