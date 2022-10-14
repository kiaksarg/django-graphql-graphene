from graphene_django.types import DjangoObjectType
from graphene import relay
from graphene_federation import key

from ...post.models import Post, Postcat
from .dataloaders import ChildrenByIdLoader, ChildByIdLoader
from ..core.connection import CountableDjangoObjectType
from .enums import PostTypeEnum, CultureEnum


@key(fields="id")
class PostType(CountableDjangoObjectType):
    # children = graphene.List(lambda:PostType)
    culture= CultureEnum()
    post_type= PostTypeEnum()

    class Meta:
        description = (
            "Create Post "
        )
        model = Post
        only_fields = [
            "title",
            "name",
            "slug",
            "parent_self",
            "children_self",
            "children",
            "post_content",
            "description",
            "mim_type",
            "author",
            "author_text",
            "order_date",
            "seo_description",
            "seo_title",
            "created_at",
            "updated_at",
        ]
        interfaces = [relay.Node]

    def resolve_children(root: Post, info, **_kwargs):
        if root.id:
            return ChildrenByIdLoader(info.context).load(root.id)
        return None


@key(fields="id")
class PostcatType(CountableDjangoObjectType):
    # children= graphene.List(lambda: PostInPostType)
    class Meta:
        model = Postcat
        interfaces = [relay.Node]

    def resolve_child(root: Postcat, info, **_kwargs):
        if root.child_id:
            return ChildByIdLoader(info.context).load(root.child_id)
        return None
