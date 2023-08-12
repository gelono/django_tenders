from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from django_tenders.permissions import IsAdminOrReadOnly
from tenders.models import Subscriber


class TenderMixin:
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly, ]  # IsAuthenticated, DKNumbersIsSubscriberOrAdmin
    filter_backends = [DjangoFilterBackend]

    def get_queryset_mixin(self, **kwargs):
        queryset = kwargs['model'].objects.select_related('customer').prefetch_related()
        if self.request.user.is_staff:
            return self.queryset
        else:
            subscriber = Subscriber.objects.get(user=self.request.user)
            return queryset.filter(dk_numbers__in=subscriber.dk_numbers.all())
