import django_filters
from src.models import Booking
from django_filters import DateFilter


class OrderFilter(django_filters.FilterSet):
    from_date = DateFilter(field_name='date', lookup_expr='gte', label='From Date')
    to_date = DateFilter(field_name='date', lookup_expr='lte', label='To Date')

    class Meta:
        model = Booking
        fields = ('from_date', 'to_date')
