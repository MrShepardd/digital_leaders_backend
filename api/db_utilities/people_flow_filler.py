import pandas as pd
from ..models import PeopleFlow, Polygon
from ..utilities import prepare_cover_date, prepare_cover_time


def get_nan_value(val, default='1901-01-01'):
    return val if val == val else default


def construct_people_flow(row, polygon, age_min, age_max):
    return PeopleFlow(
        square_id=polygon,
        sex=int(row['sex']),
        age_min=age_min,
        age_max=age_max,
        date=prepare_cover_date(row['date']),
        time=prepare_cover_time(row['time']),
        abnt_cnt=float(get_nan_value(row['abnt_cnt'], '-1.0')),
    )


class PeopleFlowFiller:
    def __init__(self, path='data/people_flow.csv', prefix=''):
        self.path = prefix + path
        self.df = pd.read_csv(self.path, delimiter=';', encoding='windows-1251')

    def refill(self):
        PeopleFlow.objects.all().delete()

        rows = []
        for (i, v) in self.df.iterrows():
            if i % 10000 == 0:
                print(i)

            polygon = Polygon.objects.get(square_id=v['square_id'])

            age = v['age'].split('_')

            if len(age) != 2:
                continue

            age_min = age[0]
            age_max = age[1] if age[1] != 'inf' else 100

            rows.append(construct_people_flow(v, polygon, age_min, age_max))

        PeopleFlow.objects.bulk_create(rows)

        print('people flow refilled')
