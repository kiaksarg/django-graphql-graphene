import graphene

from .types import Site


class SiteQueries(graphene.ObjectType):
    site = graphene.Field(
        Site, description="Return information about the site.", required=True
    )

    def resolve_site(self, _info):
        return Site()
