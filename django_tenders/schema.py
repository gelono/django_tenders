import graphene
from graphql import GraphQLResolveInfo

from tenders.models import ActiveTender
from tenders.schema import ActiveTenderType


class Query(graphene.ObjectType):
    tenders = graphene.List(ActiveTenderType, first=graphene.Int())
    tender_by_name = graphene.Field(ActiveTenderType, tender_name=graphene.String())
    tender_by_status = graphene.List(ActiveTenderType, status=graphene.String())

    def resolve_tender_by_name(self, info: GraphQLResolveInfo, tender_name: str):
        return ActiveTender.objects.filter(tender_name=tender_name).first()

    def resolve_tender_by_status(self, info: GraphQLResolveInfo, status: str):
        return ActiveTender.objects.all().filter(status=status)

    def resolve_tenders(self, info: GraphQLResolveInfo, first: int = None):
        tenders = ActiveTender.objects.all()

        if first:
            return tenders[:first]
        else:
            return tenders


schema = graphene.Schema(query=Query)
