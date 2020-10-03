import pandas as pd
from ..models import CrowdedPlace


def get_nan_value(val, default='1901-01-01'):
    return val if val == val else default


def construct_crowded_place(row, place_type):
    return CrowdedPlace(
        name=row['name'],
        gis_id=row['gis_id'],
        type=place_type,
        address=row['address'],
        lat=float(get_nan_value(row['lat'], '-1.0')),
        lon=float(get_nan_value(row['lon'], '-1.0'))
    )


class CrowdedPlaceFiller:
    def __init__(self, path='data/stops.xlsx', prefix=''):
        self.path = prefix + path
        self.df = pd.read_excel(self.path)

    def refill(self):
        CrowdedPlace.objects.all().delete()

        rows = []
        for (i, v) in self.df.iterrows():
            if i % 100 == 0:
                print(i)

            place_type = 'bus_stop'

            rows.append(construct_crowded_place(v, place_type))

        CrowdedPlace.objects.bulk_create(rows)

        print('crowded places refilled')
