import graphene
from django.contrib.auth import get_user_model, models as auth_models
from graphene import relay
from graphene_federation import key
from graphql_jwt.exceptions import PermissionDenied

from ...account import models
from ...core.permissions import AccountPermissions
from ..core.connection import CountableDjangoObjectType
from ..core.fields import PrefetchingConnectionField
from ..core.types import Image, Permission
from ..core.utils import from_global_id_strict_type
from ..decorators import one_of_permissions_required, permission_required
from ..meta.deprecated.resolvers import resolve_meta, resolve_private_meta
from ..meta.types import ObjectWithMetadata
from ..utils import format_permissions_for_display
from .utils import can_user_manage_group, get_groups_which_user_can_manage



class UserPermission(Permission):
    source_permission_groups = graphene.List(
        graphene.NonNull("zagros.gql.account.types.Group"),
        description="List of user permission groups which contains this permission.",
        user_id=graphene.Argument(
            graphene.ID,
            description="ID of user whose groups should be returned.",
            required=True,
        ),
        required=False,
    )

    def resolve_source_permission_groups(root: Permission, _info, user_id, **_kwargs):
        user_id = from_global_id_strict_type(user_id, only_type="User", field="pk")
        groups = auth_models.Group.objects.filter(
            user__pk=user_id, permissions__name=root.name
        )
        return groups


@key("id")
@key("email")
class User(CountableDjangoObjectType):

    note = graphene.String(description="A note about the user.")
    first_name = graphene.String(description="User firstname.")

    user_permissions = graphene.List(
        UserPermission, description="List of user's permissions."
    )
    permission_groups = graphene.List(
        "zagros.gql.account.types.Group",
        description="List of user's permission groups.",
    )
    editable_groups = graphene.List(
        "zagros.gql.account.types.Group",
        description="List of user's permission groups which user can manage.",
    )
    avatar = graphene.Field(Image, size=graphene.Int(description="Size of the avatar."))


    class Meta:
        description = "Represents user data."
        interfaces = [relay.Node, ObjectWithMetadata]
        model = get_user_model()
        only_fields = [
            "date_joined",
            "email",
            "phone",
            "first_name",
            "id",
            "is_active",
            "is_staff",
            "last_login",
            "last_name",
            "note",
        ]


    @staticmethod
    def resolve_permissions(root: models.User, _info, **_kwargs):
        # deprecated, to remove in #5389
        from .resolvers import resolve_permissions

        return resolve_permissions(root)

    @staticmethod
    def resolve_user_permissions(root: models.User, _info, **_kwargs):
        from .resolvers import resolve_permissions

        return resolve_permissions(root)

    @staticmethod
    def resolve_permission_groups(root: models.User, _info, **_kwargs):
        return root.groups.all()

    @staticmethod
    def resolve_editable_groups(root: models.User, _info, **_kwargs):
        return get_groups_which_user_can_manage(root)

    @staticmethod
    @one_of_permissions_required(
        [AccountPermissions.MANAGE_USERS, AccountPermissions.MANAGE_STAFF]
    )
    def resolve_note(root: models.User, info):
        return root.note

    @staticmethod
    @one_of_permissions_required(
        [AccountPermissions.MANAGE_USERS, AccountPermissions.MANAGE_STAFF]
    )
    def resolve_events(root: models.User, info):
        return root.events.all()

    @staticmethod
    def resolve_avatar(root: models.User, info, size=None, **_kwargs):
        if root.avatar:
            return Image.get_adjusted(
                image=root.avatar,
                alt=None,
                size=size,
                rendition_key_set="user_avatars",
                info=info,
            )

    @staticmethod
    @one_of_permissions_required(
        [AccountPermissions.MANAGE_USERS, AccountPermissions.MANAGE_STAFF]
    )
    def resolve_private_meta(root: models.User, _info):
        return resolve_private_meta(root, _info)

    @staticmethod
    def resolve_meta(root: models.User, _info):
        return resolve_meta(root, _info)

    @staticmethod
    def __resolve_reference(root, _info, **_kwargs):
        if root.id is not None:
            return graphene.Node.get_node_from_global_id(_info, root.id)
        return get_user_model().objects.get(email=root.email)


class ChoiceValue(graphene.ObjectType):
    raw = graphene.String()
    verbose = graphene.String()


@key(fields="id")
class Group(CountableDjangoObjectType):
    users = graphene.List(User, description="List of group users")
    permissions = graphene.List(Permission, description="List of group permissions")
    user_can_manage = graphene.Boolean(
        required=True,
        description=(
            "True, if the currently authenticated user has rights to manage a group."
        ),
    )

    class Meta:
        description = "Represents permission group data."
        interfaces = [relay.Node]
        model = auth_models.Group
        only_fields = ["name", "permissions", "id"]

    @staticmethod
    @permission_required(AccountPermissions.MANAGE_STAFF)
    def resolve_users(root: auth_models.Group, _info):
        return root.user_set.all()

    @staticmethod
    def resolve_permissions(root: auth_models.Group, _info):
        permissions = root.permissions.prefetch_related("content_type").order_by(
            "codename"
        )
        return format_permissions_for_display(permissions)

    @staticmethod
    def resolve_user_can_manage(root: auth_models.Group, info):
        user = info.context.user
        return can_user_manage_group(user, root)
