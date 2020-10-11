import pandas as pd
from ..models import CrowdedPlace, Polygon


def get_nan_value(val, default='1901-01-01'):
    return val if val == val else default


def construct_crowded_place(row, polygon):
    return CrowdedPlace(
        name=row['name'],
        gis_id=row['gis_id'],
        square_id=polygon,
        type=row['type'],
        address=row['address'],
        lat=float(get_nan_value(row['lat'], '-1.0')),
        lon=float(get_nan_value(row['lon'], '-1.0'))
    )


class CrowdedPlaceFiller:
    def __init__(self, path='data/crowded_places.xlsx', prefix=''):
        self.path = prefix + path
        self.df = pd.read_excel(self.path)

    def refill(self):
        CrowdedPlace.objects.all().delete()

        polygons = {str(polygon.square_id): polygon for polygon in Polygon.objects.all()}

        rows = []
        for (i, v) in self.df.iterrows():
            if i % 100 == 0:
                print(i)

            square_id = str(v['square_id'])

            if square_id in polygons.keys():
                polygon = polygons[square_id]
            else:
                continue

            rows.append(construct_crowded_place(v, polygon))

        CrowdedPlace.objects.bulk_create(rows)

        print('crowded places refilled')
