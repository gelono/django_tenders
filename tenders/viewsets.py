import requests
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from django_tenders.permissions import DKNumbersIsSubscriberOrAdmin, BalanceIsAdmin, IsAdminOrReadOnly, \
    IsAdminOrReadAndPutOnly
from tenders.models import ArchiveTender, Customer, Subscriber, Winner, SubscriberBalance, TransactionIn, \
    ExtendedCompanyData
from tenders.serializers import ArchiveTenderSerializer, CustomerSerializer, WinnerSerializer, \
    SubscriberBalanceSerializer, TransactionInSerializer, ExtendedCompanyDataSerializer, TransactionOutSerializer


class ArchiveTenderViewSet(ModelViewSet):
    serializer_class = ArchiveTenderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly, ]  # IsAuthenticated, DKNumbersIsSubscriberOrAdmin

    queryset = ArchiveTender.objects.select_related('customer').prefetch_related('dk_numbers')

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        else:
            subscriber = Subscriber.objects.get(user=self.request.user)
            return self.queryset.filter(dk_numbers__in=subscriber.dk_numbers.all())


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class WinnerViewSet(ModelViewSet):
    queryset = Winner.objects.all()
    serializer_class = WinnerSerializer


class BalanceViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrReadAndPutOnly, ]  # IsAdminOrReadOnly, BalanceIsAdmin,
    serializer_class = SubscriberBalanceSerializer
    queryset = SubscriberBalance.objects.all()

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        else:
            user = self.request.user
            subscriber = Subscriber.objects.get(user=user)
            return self.queryset.filter(subscriber=subscriber)


class TransactionInView(APIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = TransactionInSerializer
    queryset = TransactionIn.objects.all()

    def get(self, request):
        user = request.user
        subscriber = Subscriber.objects.get(user=user)
        subscriber_balance = SubscriberBalance.objects.get(subscriber=subscriber)
        data = self.queryset.filter(subscriber_balance=subscriber_balance)
        serializer = TransactionInSerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        user = request.user
        subscriber = Subscriber.objects.get(user=user)
        user_subscriber_balance = SubscriberBalance.objects.get(subscriber=subscriber)
        serializer = TransactionInSerializer(data=request.data)
        if serializer.is_valid():
            transaction = serializer.save(subscriber_balance=user_subscriber_balance)
            subscriber_balance = transaction.subscriber_balance
            subscriber_balance.current_balance += transaction.amount
            subscriber_balance.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExtendedCompanyDataView(APIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = ExtendedCompanyDataSerializer
    queryset = ExtendedCompanyData.objects.all()

    def get(self, request):
        user = request.user
        subscriber = Subscriber.objects.get(user=user)
        subscriber_balance = SubscriberBalance.objects.get(subscriber=subscriber)
        user_subscriber_balance = subscriber_balance.current_balance

        if user_subscriber_balance >= 10:
            company_id = request.query_params.get('id')
            try:
                data = self.queryset.get(id=company_id)
            except ObjectDoesNotExist:
                data = None

            if data:
                serializer = ExtendedCompanyDataSerializer(data)

                trans_data = {
                    'amount': 10,
                    'currency': 'UAH'
                }
                serializer_out = TransactionOutSerializer(data=trans_data)
                if serializer_out.is_valid():
                    transaction = serializer_out.save(subscriber_balance=subscriber_balance)
                    subscriber_balance.current_balance -= transaction.amount
                    subscriber_balance.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response('The company was not found', status=status.HTTP_400_BAD_REQUEST)

        return Response('The lack of funds', status=status.HTTP_400_BAD_REQUEST)