from django.urls import path
from crm.views.noncoliver_views import apply_noncoliver
from crm.views.coliver_views import coliver_list



urlpatterns = [
    path("colivers/", coliver_list, name="coliver_list"),
]

urlpatterns = [
    path("apply/", apply_noncoliver, name="apply"),
]