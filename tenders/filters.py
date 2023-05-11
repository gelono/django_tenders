from django_filters import FilterSet, CharFilter

from tenders.models import ArchiveTender, Customer, Winner, ActiveTender


class ArchiveTenderFilter(FilterSet):
    tender_name = CharFilter(field_name='tender_name', lookup_expr='icontains')

    class Meta:
        model = ArchiveTender
        fields = ['tender_name', 'status', ]


class ActiveTenderFilter(FilterSet):
    tender_name = CharFilter(field_name='tender_name', lookup_expr='icontains')

    class Meta:
        model = ActiveTender
        fields = ['tender_name', 'status', ]


class CustomerFilter(FilterSet):
    customer_name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Customer
        fields = ['name', 'edrpou', ]


class WinnerFilter(FilterSet):
    winner_name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Winner
        fields = ['name', ]
