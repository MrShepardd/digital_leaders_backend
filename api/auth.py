from django.http import JsonResponse

user_obj = {
    'id': 1,
    'email': 'admin@admin.ru',
    'full_name': 'admin',
}

allowed_pages = [
    'dashboard'
]


def check_auth(request):

    token = request.GET.get('token')
    authorized = True if token == '15aada70a60bcbb156459c75d9bea50e' else False

    auth = {
        'success': authorized,
        'user': user_obj if authorized else {},
        'allowed_pages': allowed_pages if authorized else []
    }

    return JsonResponse(auth)
