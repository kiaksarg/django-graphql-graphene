import graphene
from django.core.exceptions import ValidationError

from ..core.mutations import BaseMutation, ModelDeleteMutation, ModelMutation
from .enums import CultureEnum, PostTypeEnum
from ...post.models import Post, Postcat
from ...core.permissions import PostPermissions
from ...post.error_codes import PostErrorCode
from ..core.types.common import PostError, SeoInput
from ..core.utils import clean_seo_fields, validate_slug_and_generate_if_needed


class PostInput(graphene.InputObjectType):
    name = graphene.String(description="Post title.")
    slug = graphene.String(description="Post internal name.")
    title = graphene.String(description="Post title.")
    post_content = graphene.String(
        description=(
            "Post content. May consist of ordinary text, HTML and images.")
    )
    description = graphene.String(
        description="Product description (HTML/text).")
    mim_type = graphene.String(description="Post mim_type.")
    author = graphene.ID(
        description="ID of the user created the post.",
        name="author",
        required=False
    )
    author_text = graphene.String(
        description="Author of the post (text).")

    culture = CultureEnum(description="Post culture.")
    post_type = PostTypeEnum(description="Post type.")
    order_date = graphene.types.datetime.DateTime(
        description="Post ordered by this date. ISO 8601 format."
    )
    seo = SeoInput(description="Search engine optimization fields.")
    # created_at = graphene.types.datetime.DateTime(
    #     description="Creation date. ISO 8601 format."
    # )
    # updated_at = graphene.types.datetime.DateTime(
    #     description="Update date. ISO 8601 format."
    # )


class PostCreate(ModelMutation):
    class Arguments:
        input = PostInput(
            required=True, description="Fields required to create a post."
        )
        parent_self_id = graphene.ID(
            description=(
                "ID of the parent_self post. If empty, post will be top level "
                "category."
            ),
            name="parent_self",
        )

    class Meta:
        description = "Creates a new post."
        model = Post
        permissions = (
            (PostPermissions.MANAGE_POSTS.codename, "Manage posts."),
            # (PostPermissions.CREATE_POSTS.codename, "Create posts."),
        )
        error_type_class = PostError
        error_type_field = "post_errors"

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)
        try:
            cleaned_input = validate_slug_and_generate_if_needed(
                instance, "title", cleaned_input
            )
        except ValidationError as error:
            error.code = PostErrorCode.REQUIRED
            raise ValidationError({"slug": error})
        clean_seo_fields(cleaned_input)
        return cleaned_input


class PostcatInput(graphene.InputObjectType):
    child = graphene.ID(
        description=(
            "ID of the child post."
        ),
        name="child",
        required=True
    )
    parent = graphene.ID(
        description=(
            "ID of the parent post."
        ),
        name="parent",
        required=True
    )
    sort_order = graphene.Int(
        description=(
            "The relative sorting position of the post (from -inf to +inf) "
            "starting from the first given post's actual position."
        )
    )

class PostcatCreate(ModelMutation):
    class Arguments:
        input = PostcatInput(
            required=True, description="Fields required to create a postcat."
        )
    class Meta:
        description = "Creates a new postcat."
        model = Postcat
        permissions = (
            (PostPermissions.MANAGE_POSTS.codename, "Manage posts."),
            (PostPermissions.MANAGE_CATS.codename, "Manage cats."),
        )
        error_type_class = PostError
        error_type_field = "post_errors"
