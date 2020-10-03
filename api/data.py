from django.http import JsonResponse
from .mercury.mercury import Mercury


def get_dashboard_data(request):
    data = Mercury().get_general_review()
    return JsonResponse(data)
