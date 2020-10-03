import datetime


def prepare_date_created(s):
    y, m, d = s[1:-1].split(',')
    return datetime.date(int(y.strip()), int(m.strip()), int(d.strip()))


def prepare_cover_date(s):
    return datetime.date(int(s[:4]), int(s[5:7]), int(s[8:]))


def prepare_cover_time(s):
    h, i, s = s.split(':')
    return datetime.time(int(h), int(i), int(s))
