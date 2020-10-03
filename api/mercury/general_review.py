import json
import pickle
import os
import datetime
import numpy as N
from django.db.models import Count


class GeneralReview:
    def __init__(self, eid='10-s2.0-60103811', prefix=''):
        self.eid = eid
