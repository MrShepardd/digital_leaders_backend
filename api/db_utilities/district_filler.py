import pandas as pd
from ..models import District


def get_nan_value(val, default='1901-01-01'):
    return val if val == val else default


def construct_district(row):
    return District(
        name=row['name'],
        gis_id=row['gis_id'],
        population=int(get_nan_value(row['population'], '-1')),
        address=row['address'],
        lat=float(get_nan_value(row['lat'], '-1.0')),
        lon=float(get_nan_value(row['lon'], '-1.0')),
        geometry=row['geometry'],
    )


class DistrictFiller:
    def __init__(self, path='data/district.xlsx', prefix=''):
        self.path = prefix + path
        self.df = pd.read_excel(self.path)

    def refill(self):
        District.objects.all().delete()

        rows = []
        for (i, v) in self.df.iterrows():
            if i % 10 == 0:
                print(i)

            rows.append(construct_district(v))

        District.objects.bulk_create(rows)

        print('district refilled')
