from django.urls import path
from .views import plasticity_report

urlpatterns = [
    path('cycle/', plasticity_report, name='plasticity_report'),
]