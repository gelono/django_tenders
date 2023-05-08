import graphene
from graphene_django import DjangoObjectType

from tenders.models import ActiveTender, Customer, DKNumber


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ('customer_name', )


class DKNumberType(DjangoObjectType):
    class Meta:
        model = DKNumber
        fields = ('dk_number', )


class ActiveTenderType(DjangoObjectType):
    customer = graphene.Field(CustomerType)
    dk_numbers = graphene.List(DKNumberType)

    class Meta:
        model = ActiveTender
        fields = ('id', 'link', 'status', 'tender_name', 'customer', 'dk_numbers')

    def resolve_dk_numbers(self, info):
        return self.dk_numbers.all()
