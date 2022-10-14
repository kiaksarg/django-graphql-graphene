from typing import Any, List

from graphql_jwt.exceptions import PermissionDenied

from ...account import models as account_models
from ...core.permissions import (
    AccountPermissions,
    BasePermissionEnum,
    PostPermissions,
)


def no_permissions(_info, _object_pk: Any) -> List[None]:
    return []


def public_user_permissions(info, user_pk: int) -> List[BasePermissionEnum]:
    """Resolve permission for access to public metadata for user.

    Customer have access to own public metadata.
    Staff user with `MANAGE_USERS` have access to customers public metadata.
    Staff user with `MANAGE_STAFF` have access to staff users public metadata.
    """
    user = account_models.User.objects.filter(pk=user_pk).first()
    if not user:
        raise PermissionDenied()
    if info.context.user.pk == user.pk:
        return []
    if user.is_staff:
        return [AccountPermissions.MANAGE_STAFF]
    return [AccountPermissions.MANAGE_USERS]


def private_user_permissions(_info, user_pk: int) -> List[BasePermissionEnum]:
    user = account_models.User.objects.filter(pk=user_pk).first()
    if not user:
        raise PermissionDenied()
    if user.is_staff:
        return [AccountPermissions.MANAGE_STAFF]
    return [AccountPermissions.MANAGE_USERS]


def post_permissions(_info, _object_pk: Any) -> List[BasePermissionEnum]:
    return [PostPermissions.MANAGE_POSTS]


def postcat_permissions(_info, _object_pk: Any) -> List[BasePermissionEnum]:
    return [PostPermissions.MANAGE_CATS]



PUBLIC_META_PERMISSION_MAP = {
    "Post": post_permissions,
    "Postcat": postcat_permissions,
    "home": no_permissions,
    "Order": no_permissions,
    "User": public_user_permissions,
}


PRIVATE_META_PERMISSION_MAP = {
    "Post": post_permissions,
    "Postcat": postcat_permissions,
    "User": private_user_permissions,
}
