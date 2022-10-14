import graphene

from ...core.permissions import AccountPermissions
from ..core.fields import FilterInputConnectionField
from ..core.types import FilterInputObjectType
from ..decorators import one_of_permissions_required, permission_required
from .bulk_mutations import CustomerBulkDelete, StaffBulkDelete, UserBulkSetActive

from .enums import CountryCodeEnum
from .filters import CustomerFilter, PermissionGroupFilter, StaffUserFilter
from .mutations.account import (
    AccountDelete,
    AccountRegister,
    AccountRequestDeletion,
    AccountUpdate,
    AccountUpdateMeta,
    ConfirmEmailChange,
    RequestEmailChange,
)
from .mutations.jwt import (
    CreateToken,
    DeactivateAllUserTokens,
    RefreshToken,
    VerifyToken,
)
from .mutations.base import (
    ConfirmAccount,
    PasswordChange,
    RequestPasswordReset,
    SetPassword,
    UserClearMeta,
    UserUpdateMeta,
)
from .mutations.permission_group import (
    PermissionGroupCreate,
    PermissionGroupDelete,
    PermissionGroupUpdate,
)
from .mutations.staff import (
    StaffCreate,
    StaffDelete,
    StaffUpdate,
    UserAvatarDelete,
    UserAvatarUpdate,
    UserClearPrivateMeta,
    UserUpdatePrivateMeta,
)
from .resolvers import (
    resolve_permission_groups,
    resolve_staff_users,
    resolve_user,
    resolve_users,
)
from .sorters import PermissionGroupSortingInput, UserSortingInput
from .types import  Group, User



class CustomerFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = CustomerFilter


class PermissionGroupFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = PermissionGroupFilter


class StaffUserInput(FilterInputObjectType):
    class Meta:
        filterset_class = StaffUserFilter


class AccountQueries(graphene.ObjectType):
    customers = FilterInputConnectionField(
        User,
        filter=CustomerFilterInput(description="Filtering options for customers."),
        sort_by=UserSortingInput(description="Sort customers."),
        description="List of the shop's customers.",
    )
    permission_groups = FilterInputConnectionField(
        Group,
        filter=PermissionGroupFilterInput(
            description="Filtering options for permission groups."
        ),
        sort_by=PermissionGroupSortingInput(description="Sort permission groups."),
        description="List of permission groups.",
    )
    permission_group = graphene.Field(
        Group,
        id=graphene.Argument(
            graphene.ID, description="ID of the group.", required=True
        ),
        description="Look up permission group by ID.",
    )
    me = graphene.Field(User, description="Return the currently authenticated user.")
    staff_users = FilterInputConnectionField(
        User,
        filter=StaffUserInput(description="Filtering options for staff users."),
        sort_by=UserSortingInput(description="Sort staff users."),
        description="List of the shop's staff users.",
    )

    user = graphene.Field(
        User,
        id=graphene.Argument(graphene.ID, description="ID of the user.", required=True),
        description="Look up a user by ID.",
    )

    # @permission_required(AppPermission.MANAGE_APPS)
    # def resolve_service_accounts(self, info, **kwargs):
    #     return resolve_service_accounts(info, **kwargs)

    # @permission_required(AppPermission.MANAGE_APPS)
    # def resolve_service_account(self, info, id):
    #     return graphene.Node.get_node_from_global_id(info, id, ServiceAccount)

    @permission_required(AccountPermissions.MANAGE_USERS)
    def resolve_users(self, info, query=None, **kwargs):
        return resolve_users(info, query=query, **kwargs)

    @permission_required(AccountPermissions.MANAGE_STAFF)
    def resolve_permission_groups(self, info, query=None, **kwargs):
        return resolve_permission_groups(info, query=query, **kwargs)

    @permission_required(AccountPermissions.MANAGE_STAFF)
    def resolve_permission_group(self, info, id):
        return graphene.Node.get_node_from_global_id(info, id, Group)

    def resolve_me(self, info):
        user = info.context.user
        return user if user.is_authenticated else None

    @permission_required(AccountPermissions.MANAGE_STAFF)
    def resolve_staff_users(self, info, query=None, **kwargs):
        return resolve_staff_users(info, query=query, **kwargs)

    @one_of_permissions_required(
        [AccountPermissions.MANAGE_STAFF, AccountPermissions.MANAGE_USERS]
    )
    def resolve_user(self, info, id):
        return resolve_user(info, id)




class AccountMutations(graphene.ObjectType):
    # Base mutations
    token_create = CreateToken.Field()
    token_refresh = RefreshToken.Field()
    token_verify = VerifyToken.Field()
    tokens_deactivate_all = DeactivateAllUserTokens.Field()

    request_password_reset = RequestPasswordReset.Field()
    confirm_account = ConfirmAccount.Field()
    set_password = SetPassword.Field()
    password_change = PasswordChange.Field()
    request_email_change = RequestEmailChange.Field()
    confirm_email_change = ConfirmEmailChange.Field()

    # Account mutations
    account_register = AccountRegister.Field()
    account_update = AccountUpdate.Field()
    account_request_deletion = AccountRequestDeletion.Field()
    account_delete = AccountDelete.Field()

    account_update_meta = AccountUpdateMeta.Field(
        deprecation_reason=(
            "Use the `updateMetadata` mutation. This field will be removed after "
            "2020-07-31."
        )
    )

    # Staff mutations

    staff_create = StaffCreate.Field()
    staff_update = StaffUpdate.Field()
    staff_delete = StaffDelete.Field()
    staff_bulk_delete = StaffBulkDelete.Field()

    user_avatar_update = UserAvatarUpdate.Field()
    user_avatar_delete = UserAvatarDelete.Field()
    user_bulk_set_active = UserBulkSetActive.Field()

    user_update_metadata = UserUpdateMeta.Field(
        deprecation_reason=(
            "Use the `updateMetadata` mutation. This field will be removed after "
            "2020-07-31."
        )
    )
    user_clear_metadata = UserClearMeta.Field(
        deprecation_reason=(
            "Use the `deleteMetadata` mutation. This field will be removed after "
            "2020-07-31."
        )
    )

    user_update_private_metadata = UserUpdatePrivateMeta.Field(
        deprecation_reason=(
            "Use the `updatePrivateMetadata` mutation. This field will be removed "
            "after 2020-07-31."
        )
    )
    user_clear_private_metadata = UserClearPrivateMeta.Field(
        deprecation_reason=(
            "Use the `deletePrivateMetadata` mutation. This field will be removed "
            "after 2020-07-31."
        )
    )

    # Permission group mutations
    permission_group_create = PermissionGroupCreate.Field()
    permission_group_update = PermissionGroupUpdate.Field()
    permission_group_delete = PermissionGroupDelete.Field()