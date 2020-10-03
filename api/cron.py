from backend.scopus_fefu import gis_atm_downloader as gad
from backend.scopus_fefu import yandex_atm_downloader as yad
from backend.scopus_fefu import yandex_district_downloader as ydd
from backend.scopus_fefu import yandex_stops_downloader as ysd
from django.http import HttpResponse

from .db_utilities.db_filler import DBFiller
from .db_utilities.bank_filler import BankFiller
from .db_utilities.district_filler import DistrictFiller
from .db_utilities.crowded_place_filler import CrowdedPlaceFiller
from .db_utilities.atm_filler import AtmFiller
from .db_utilities.atm_crowded_place_filler import AtmCrowdedPlaceFiller
from .db_utilities.polygon_filler import PolygonFiller
from .db_utilities.people_flow_filler import PeopleFlowFiller

from .mercury.general_review import GeneralReview

import pickle
import pandas as pd
import datetime
import os
from datetime import date

PRODUCTION_PATH = '/home/dashboard-for-science-backend/'


def create_backup_directory(path, date):
    if not os.path.isdir(path + 'snapshots'):
        os.mkdir(path + 'snapshots')

    if not os.path.isdir(path + 'snapshots/' + date):
        os.mkdir(path + 'snapshots/' + date)


def get_prefix_and_date(production):
    prefix = PRODUCTION_PATH if production else ''
    str_date = date.today()
    str_date = str_date.strftime('%Y-%m-%d')
    return prefix, str_date


def download_all_stops(production=True):
    print(str(datetime.datetime.now()) + '; start: download_all_atms')

    prefix, str_date = get_prefix_and_date(production)
    create_backup_directory(prefix + 'data/', str_date)

    with open('data/stops-yandex.txt') as f:
        stop_list = [line.split() for line in f]

    stops = [item for sublist in stop_list for item in sublist]

    dd = ysd.StopDownloader(stops=stops)
    dd.download_stop()

    dd.save_to_file(name=prefix + 'data/stops.xlsx')
    dd.save_to_file(name=prefix + 'data/snapshots/' + str_date + '/stops.xlsx')

    print(str(datetime.datetime.now()) + '; end: download_all_stops')

    return HttpResponse("Hello, world. You're at the polls index.")


def download_all_district(production=True):
    print(str(datetime.datetime.now()) + '; start: download_all_atms')

    prefix, str_date = get_prefix_and_date(production)
    create_backup_directory(prefix + 'data/', str_date)

    dd = ydd.DistrictDownloader()
    dd.download_district()

    dd.save_to_file(name=prefix + 'data/district.xlsx')
    dd.save_to_file(name=prefix + 'data/snapshots/' + str_date + '/district.xlsx')

    print(str(datetime.datetime.now()) + '; end: download_all_districts')

    return HttpResponse("Hello, world. You're at the polls index.")


def download_all_atm(production=True):
    print(str(datetime.datetime.now()) + '; start: download_all_atms')

    prefix, str_date = get_prefix_and_date(production)
    create_backup_directory(prefix + 'data/', str_date)

    with open('data/atm-list-yandex.txt') as f:
        url_list = [line.split() for line in f]

    urls = [item for sublist in url_list for item in sublist]

    ad = yad.AtmDownloader(urls=urls)
    ad.download_atm()

    ad.save_to_file(name=prefix + 'data/atm.xlsx')
    ad.save_to_file(name=prefix + 'data/snapshots/' + str_date + '/atm.xlsx')
    ad.save_banks_to_file(name=prefix + 'data/banks.xlsx')
    ad.save_banks_to_file(name=prefix + 'data/snapshots/' + str_date + '/banks.xlsx')

    print(str(datetime.datetime.now()) + '; end: download_all_atms')

    return HttpResponse("Hello, world. You're at the polls index.")


def refill_db(production=True):
    print(str(datetime.datetime.now()) + '; start: refill_db')

    prefix = PRODUCTION_PATH if production else ''

    db_filler = DBFiller()
    db_filler.add_instance(DistrictFiller(prefix=prefix))
    db_filler.add_instance(BankFiller(prefix=prefix))
    db_filler.add_instance(AtmFiller(prefix=prefix))
    db_filler.add_instance(CrowdedPlaceFiller(prefix=prefix))
    db_filler.add_instance(AtmCrowdedPlaceFiller(prefix=prefix))
    db_filler.add_instance(PolygonFiller(prefix=prefix))
    db_filler.add_instance(PeopleFlowFiller(prefix=prefix))

    db_filler.refill()

    print(str(datetime.datetime.now()) + '; end: refill_db')

    return HttpResponse("Hello, world. You're at the polls index.")


def make_pre_calculation(production=True):
    prefix = PRODUCTION_PATH if production else ''

    return HttpResponse("Hello, world. You're at the polls index.")
