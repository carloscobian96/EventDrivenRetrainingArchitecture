from django.urls import path
from .views import plasticity_report, plasticity_diagram

urlpatterns = [
    path('cycle/', plasticity_report, name='plasticity_report'),
    path('diagram/', plasticity_diagram, name='plasticity_diagram'),
]