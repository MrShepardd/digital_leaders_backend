from django.http import JsonResponse
from .science.science import Science

from api.cron import refill_db, download_all_atm, download_all_district, download_all_stops

user_obj = {
    'id': 1,
    'email': 'admin@admin.ru',
    'full_name': 'admin',
}

allowed_pages = [
    'dashboard', 'authors', 'citation', 'magazines', 'knowledge', 'affiliations', 'developing', 'profile',
    'graph'
]


def check_auth(request):

    token = request.GET.get('token')
    authorized = True if token == '15aada70a60bcbb156459c75d9bea50e' else False

    auth = {
        'success': authorized,
        'user': user_obj if authorized else {},
        'allowed_pages': allowed_pages if authorized else []
    }

    refill_db(production=False)
    # download_all_stops(production=False)

    return JsonResponse(auth)
