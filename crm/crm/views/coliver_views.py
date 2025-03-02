from django.shortcuts import render
from crm.models.coliver import Coliver

def coliver_list(request):
    colivers = Coliver.objects.all()
    return render(request, "crm/coliver_list.html", {"colivers": colivers})
