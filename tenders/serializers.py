from django.contrib.auth.models import User
from rest_framework import serializers

from tenders.models import ArchiveTender, Customer, DKNumber, Winner, SubscriberBalance, TransactionIn, \
    ExtendedCompanyData, TransactionOut, ActiveTender


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'name', 'edrpou')


class WinnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Winner
        fields = ('id', 'name')


class DKNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = DKNumber
        fields = ('dk',)


class ArchiveTenderSerializer(serializers.ModelSerializer):
    dk_numbers = DKNumberSerializer(many=True)
    customer = CustomerSerializer()

    class Meta:
        model = ArchiveTender
        fields = ('id', 'tender_name', 'status', 'dk_numbers', 'customer')


class ActiveTenderSerializer(serializers.ModelSerializer):
    dk_numbers = DKNumberSerializer(many=True)
    customer = CustomerSerializer()

    class Meta:
        model = ActiveTender
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
    username = UserSerializer(source='subscriber_balance.subscriber.user', read_only=True)

    class Meta:
        model = TransactionIn
        fields = ('id', 'created', 'amount', 'currency', 'username')


class TransactionOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionOut
        fields = ('id', 'created', 'amount', 'currency')


class ExtendedCompanyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtendedCompanyData
        fields = ('id', 'fullname', 'shortname', 'location', 'email', 'primary_activity', 'ceo_name', 'capital')


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "password")

        def create(self, validated_data):
            user = User.objects.create(
                username=validated_data['username'],
                password=validated_data['password'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name']
            )
            return user
