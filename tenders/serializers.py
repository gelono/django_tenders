from django.contrib.auth.models import User
from rest_framework import serializers

from tenders.models import ArchiveTender, Customer, DKNumber, Winner, SubscriberBalance, TransactionIn, \
    ExtendedCompanyData, TransactionOut


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('customer_name', 'customer_edrpou')


class WinnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Winner
        fields = ('winner_name', )


class DKNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = DKNumber
        fields = ('dk_number',)


class ArchiveTenderSerializer(serializers.ModelSerializer):
    dk_numbers = DKNumberSerializer(many=True)
    customer = CustomerSerializer()

    class Meta:
        model = ArchiveTender
        fields = ('id', 'tender_name', 'status', 'dk_numbers', 'customer')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', )


class SubscriberBalanceSerializer(serializers.ModelSerializer):
    username = UserSerializer(source='subscriber.user', read_only=True)

    class Meta:
        model = SubscriberBalance
        fields = ('id', 'subscriber', 'current_balance', 'currency', 'username')


class TransactionInSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionIn
        fields = ('id', 'created', 'amount', 'currency')


class TransactionOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionOut
        fields = ('id', 'created', 'amount', 'currency')


class ExtendedCompanyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtendedCompanyData
        fields = ('id', 'fullname', 'shortname', 'location', 'email', 'primary_activity', 'ceo_name', 'capital')
