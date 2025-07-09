# fichajeRemoto -> views.py 

from django.shortcuts import render
# Create your views here.
from django.http import HttpResponse



def fichajeRemotoHome(request):
    return render(request, "fichajeRemoto/fichaje.html", {})

