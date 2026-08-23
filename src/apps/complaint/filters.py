import django_filters
from .models import Complaint


class Filtering(django_filters.FilterSet):

    class Meta:
        model=Complaint
        fields={
            "status":['iexact'],
            'priority':['exact'],
            'category':['icontains']
        }
