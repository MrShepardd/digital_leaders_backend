from django.http import JsonResponse
from .science.science import Science


def get_affiliation_data(request):
    data = Science().get_affiliation_review()
    return JsonResponse(data)

def get_author_data(request):
    data = Science().get_author_review()
    return JsonResponse(data)

def get_citation_data(request):
    data = Science().get_citation_review()
    return JsonResponse(data)

def get_dashboard_data(request):
    data = Science().get_general_review()
    return JsonResponse(data)

def get_knowledge_data(request):
    data = Science().get_knowledge_review()
    return JsonResponse(data)

def get_journal_data(request):
    data = Science().get_journal_review()
    return JsonResponse(data)