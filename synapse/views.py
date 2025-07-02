from django.shortcuts import render
from .models import Synapse

def plasticity_report(request):
    syn = Synapse.objects.first()
    return render(request, 'synapse/plasticity_report.html', {'synapse': syn})
