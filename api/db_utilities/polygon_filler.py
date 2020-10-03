import pandas as pd
from ..models import District, Polygon


def get_nan_value(val, default='1901-01-01'):
    return val if val == val else default


def construct_polygon(row, district):
    return Polygon(
        square_id=row['square_id'],
        district=district,
        wkt_geo=row['wkt_geo'],
    )


class PolygonFiller:
    def __init__(self, path='data/polygons.csv', prefix=''):
        self.path = prefix + path
        self.df = pd.read_csv(self.path, delimiter=';', encoding='windows-1251')

    def refill(self):
        Polygon.objects.all().delete()

        rows = []
        for (i, v) in self.df.iterrows():
            if i % 10000 == 0:
                print(i)

            district = District.objects.get(name=v['district'])
            # print(v['square_id'])
            rows.append(construct_polygon(v, district))

        Polygon.objects.bulk_create(rows)

        print('Polygons refilled')
