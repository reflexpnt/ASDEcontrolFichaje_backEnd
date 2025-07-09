# fichajeRemoto -> urls.py 

from django.urls import path
from fichajeRemoto import views

urlpatterns = [
    path("", views.fichajeRemotoHome, name="fichajeRemotoHome"),
]