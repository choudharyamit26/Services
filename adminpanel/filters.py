import django_filters
from src.models import Booking
from django_filters import DateFilter


class OrderFilter(django_filters.FilterSet):
    from_date = DateFilter(field_name='date', lookup_expr='gte', label='From Date')
    to_date = DateFilter(field_name='date', lookup_expr='lte', label='To Date')

    class Meta:
        model = Booking
        fields = ('from_date', 'to_date')


class OrderFilter2(django_filters.FilterSet):
    order_on_from_date = DateFilter(field_name='created_at', lookup_expr='gte', label='From Date')
    order_on_to_date = DateFilter(field_name='created_at', lookup_expr='lte', label='To Date')

    class Meta:
        model = Booking
        fields = ('order_on_from_date', 'order_on_to_date')
