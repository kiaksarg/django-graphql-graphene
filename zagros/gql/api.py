import graphene
from graphene_federation import build_schema
from graphene_django.debug import DjangoDebug

from .account.schema import AccountMutations, AccountQueries
from .post.schemas import PostQueries, PostInPostQueries, PostMutations
from .core.schema import CoreMutations, CoreQueries
from .meta.schema import MetaMutations
from .site.schema import SiteQueries


class Query(
    AccountQueries,
    CoreQueries,
    PostQueries,
    PostInPostQueries,
    SiteQueries
):
    debug = graphene.Field(DjangoDebug, name='_debug')


class Mutation(
    AccountMutations,
    CoreMutations,
    MetaMutations,
    PostMutations
):
    pass


schema = build_schema(Query, mutation=Mutation)
