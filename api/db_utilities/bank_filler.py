import pandas as pd
from ..models import Bank


def get_nan_value(val, default='1901-01-01'):
    return val if val == val else default


class BankFiller:
    def __init__(self, path='data/banks.xlsx', prefix=''):
        self.path = prefix + path
        self.df = pd.read_excel(self.path)

    def refill(self):
        Bank.objects.all().delete()

        rows = []
        for (i, v) in self.df.iterrows():
            if i % 1000 == 0:
                print(i)

            rows.append(Bank(name=v['name']))

        Bank.objects.bulk_create(rows)

        print('atm refilled')
