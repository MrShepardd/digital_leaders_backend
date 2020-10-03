from django.urls import path

from api import cron, auth, data

urlpatterns = [
    path('refill_db/', cron.refill_db),
    path('auth_check/', auth.check_auth),
    path('dashboard_data/', data.get_dashboard_data)
]
