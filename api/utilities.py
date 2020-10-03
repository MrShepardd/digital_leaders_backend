import datetime


def normalize_region(s):
    s = str(s)
    if 'Altai' in s:
        s = 'Altai'
    elif 'Arkhangelsk' in s:
        s = 'Arkhangelskaya Oblast'
    elif 'Bryansk' in s:
        s = 'Bryanskaya Oblast'
    elif 'Celjabinsk' in s or 'Chelyabinsk' in s:
        s = 'Chelyabinskaya Oblast'
    elif 'Chuvash' in s:
        s = 'Chuvashia'
    elif 'Irkutsk' in s:
        s = 'Irkutskaya Oblast'
    elif 'Ivanov' in s:
        s = 'Ivanovskaya Oblast'
    elif 'Jaroslavl' in s or 'Yaroslavl' in s:
        s = 'Yaroslavl Oblast'
    elif 'Kabardino' in s:
        s = 'Kabardino-Balkariya'
    elif 'Karacha' in s:
        s = 'Karachaevo-Cherkesskaya Republic'
    elif 'Kemerovo' in s:
        s = 'Kemerovo Oblast'
    elif 'Komi' in s:
        s = 'Komi Oblast'
    elif 'Kostroma' in s:
        s = 'Kostroma Oblast'
    elif 'Krasnoyarsk' in s:
        s = 'Krasnoyarsk Krai'
    elif 'Kurgan' in s:
        s = 'Kurgan Oblast'
    elif 'Kursk' in s:
        s = 'Kurskaya Oblast'
    elif 'Lening' in s or 'Petersburg' in s:
        s = 'Leningrad Oblast'
    elif 'MO' in s or 'Moscow' in s:
        s = 'Moscow Oblast'
    elif 'Nizhny' in s:
        s = 'Nizhny Novgorod Oblast'
    elif 'Orel' in s or 'Oryol' in s:
        s = 'Orel Oblast'
    elif 'Orenburg' in s:
        s = 'Orenburg Oblast'
    elif 'Perm' in s:
        s = 'Perm Krai'
    elif 'Primor' in s or 'Vladivostok' in s:
        s = 'Primorsky Krai'
    elif 'Pskov' in s:
        s = 'Pskov Oblast'
    elif 'Tatarstan' in s:
        s = 'Tatarstan Republic'
    elif 'Adyge' in s:
        s = 'Adygea Republic'
    elif 'Kalmyk' in s:
        s = 'Kalmyk Republic'
    elif 'Karelia' in s:
        s = 'Karelia'
    elif 'Khakas' in s:
        s = 'Khakassiya Republic'
    elif 'Ossetia' in s:
        s = 'North Ossetia-Alania'
    elif 'Tuva' in s:
        s = 'Tuva Republic'
    elif 'Rostov' in s:
        s = 'Rostov Republic'
    elif 'Sakha' in s and 'Sakhalin' not in s:
        s = 'Sakha Republic'
    elif 'Samar' in s:
        s = 'Samarskaya Oblast'
    elif 'Saratov' in s:
        s = 'Saratov Oblast'
    elif 'Smolensk' in s:
        s = 'Smolenskaya Oblast'
    elif 'Serdlovskaya' in s or 'Sverdlovsk' in s:
        s = 'Sverdlovskaya Oblast'
    elif 'Tambov' in s:
        s = 'Tambov Oblast'
    elif 'Buryatia' in s:
        s = 'Buryatia Republic'
    elif 'Tyumen' in s:
        s = 'Tyumen Oblast'
    elif 'Udmurt' in s:
        s = 'Udmurt Republic'
    elif 'Volgograd' in s or 'Volvograd' in s:
        s = 'Volgograd Oblast'
    elif 'Vologda' in s:
        s = 'Vologda Oblast'
    elif 'Zabaykalsky' in s:
        s = 'Zabaykalsky Krai'
    elif 'Chechen' in s:
        s = 'Chechen Republic'
    elif 'Daghestan' in s or 'Dagestan' in s:
        s = 'Dagestan Republic'
    elif 'Mari' in s:
        s = 'Mari El Republic'
    elif 'Novosibirsk' in s:
        s = 'Novosibirsk Oblast'
    elif 'nan' in s:
        s = '__unspecified__'
    return s


def prepare_date_created(s):
    y, m, d = s[1:-1].split(',')
    return datetime.date(int(y.strip()), int(m.strip()), int(d.strip()))


def prepare_cover_date(s):
    return datetime.date(int(s[:4]), int(s[5:7]), int(s[8:]))
