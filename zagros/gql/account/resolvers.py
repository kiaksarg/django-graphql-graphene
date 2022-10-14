from itertools import chain
from typing import Optional

import graphene
from django.contrib.auth import models as auth_models
from graphql_jwt.exceptions import PermissionDenied

from ...account import models
from ...core.permissions import AccountPermissions

from ..utils import format_permissions_for_display, get_user_or_app_from_context
from ..utils.filters import filter_by_query_param
from .types import ChoiceValue
from .utils import (
    get_allowed_fields_camel_case,
    get_required_fields_camel_case,
    get_user_permissions,
)

USER_SEARCH_FIELDS = (
    "email",
    "first_name",
    "last_name"
)


def resolve_users(info, query, **_kwargs):
    qs = models.User.objects.users()
    qs = filter_by_query_param(
        queryset=qs, query=query, search_fields=USER_SEARCH_FIELDS
    )
    return qs.distinct()


def resolve_permission_groups(info, **_kwargs):
    return auth_models.Group.objects.all()


def resolve_staff_users(info, query, **_kwargs):
    qs = models.User.objects.staff()
    qs = filter_by_query_param(
        queryset=qs, query=query, search_fields=USER_SEARCH_FIELDS
    )
    return qs.distinct()


def resolve_user(info, id):
    requester = get_user_or_app_from_context(info.context)
    if requester:
        _model, user_pk = graphene.Node.from_global_id(id)
        if requester.has_perms(
            [AccountPermissions.MANAGE_STAFF, AccountPermissions.MANAGE_USERS]
        ):
            return models.User.objects.filter(pk=user_pk).first()
        if requester.has_perm(AccountPermissions.MANAGE_STAFF):
            return models.User.objects.staff().filter(pk=user_pk).first()
        if requester.has_perm(AccountPermissions.MANAGE_USERS):
            return models.User.objects.customers().filter(pk=user_pk).first()
    return PermissionDenied()



def resolve_permissions(root: models.User):
    permissions = get_user_permissions(root)
    permissions = permissions.prefetch_related("content_type").order_by("codename")
    return format_permissions_for_display(permissions)
