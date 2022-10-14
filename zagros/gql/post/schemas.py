import graphene

from ..core.fields import FilterInputConnectionField
from .types import PostType, PostcatType
from ...post.models import Post, Postcat
from .mutations import PostCreate, PostcatCreate
from .sorters import PostSortingInput
from .filters import PostFilterInput

class PostQueries(graphene.ObjectType):
    post = graphene.Field(PostType,
                          id=graphene.ID())
    posts = FilterInputConnectionField(
        PostType,
        sort_by=PostSortingInput(description="Sort posts."),
        filter=PostFilterInput(description="Filtering options for posts."),
        description="List of the posts.",
    )

    def resolve_posts(self, info, **kwargs):
        return Post.objects.all()

    def resolve_post(self, inf, **kwargs):
        id = kwargs.get('id')
        only_type, pk = graphene.Node.from_global_id(id)
        return Post.objects.get(pk=pk)


class PostInPostQueries(graphene.ObjectType):
    postcat = graphene.Field(PostcatType,
                                id=graphene.ID()
                                )
    postcats = graphene.List(PostcatType)

    def resolve_postcats(self, info, **kwargs):
        return Postcat.objects.all()

    def resolve_postcat(self, inf, **kwargs):
        id = kwargs.get('id')
        only_type, pk = graphene.Node.from_global_id(id)
        return Postcat.objects.get(pk=pk)


class PostMutations(graphene.ObjectType):
    post_create = PostCreate.Field()
    postcat_create = PostcatCreate.Field()
    # page_delete = PageDelete.Field()
    # page_bulk_delete = PageBulkDelete.Field()
    # page_bulk_publish = PageBulkPublish.Field()
    # page_update = PageUpdate.Field()
    # page_translate = PageTranslate.Field()
