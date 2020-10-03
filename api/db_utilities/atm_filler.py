import pandas as pd
from ..models import ATM, Bank


def get_nan_value(val, default='1901-01-01'):
    return val if val == val else default


def construct_atm(row, bank):
    return ATM(
        gis_id=row['gis_id'],
        name=row['name'],
        bank=bank,
        address=row['address'],
        lat=float(get_nan_value(row['lat'], '-1.0')),
        lon=float(get_nan_value(row['lon'], '-1.0')),
        schedule=row['schedule'],
    )


class AtmFiller:
    def __init__(self, path='data/atm.xlsx', prefix=''):
        self.path = prefix + path
        self.df = pd.read_excel(self.path)

    def refill(self):
        ATM.objects.all().delete()

        rows = []
        for (i, v) in self.df.iterrows():
            if i % 10000 == 0:
                print(i)

            bank = Bank.objects.get(name=v['bank'])

            rows.append(construct_atm(v, bank))

        ATM.objects.bulk_create(rows)

        print('atm refilled')
