from operator import itemgetter

from graphql_jwt.exceptions import PermissionDenied

from ...account import models as account_models
from ...core.models import ModelWithMetadata
from ..utils import get_user_or_app_from_context
from .permissions import PRIVATE_META_PERMISSION_MAP


def resolve_object_with_metadata_type(instance: ModelWithMetadata):
    # Imports inside resolvers to avoid circular imports.
    from ..account import types as account_types

    MODEL_TO_TYPE_MAP = {
        account_models.User: account_types.User,
    }
    return MODEL_TO_TYPE_MAP.get(type(instance), None)


def resolve_metadata(metadata: dict):
    return sorted(
        [{"key": k, "value": v} for k, v in metadata.items()], key=itemgetter("key"),
    )


def resolve_private_metadata(root: ModelWithMetadata, info):
    item_type = resolve_object_with_metadata_type(root)
    if not item_type:
        raise NotImplementedError(
            f"Model {type(root)} can't be mapped to type with metadata. "
            "Make sure that model exists inside MODEL_TO_TYPE_MAP."
        )

    get_required_permission = PRIVATE_META_PERMISSION_MAP[item_type.__name__]
    if not get_required_permission:
        raise PermissionDenied()

    required_permission = get_required_permission(info, root.pk)
    if not required_permission:
        raise PermissionDenied()

    requester = get_user_or_app_from_context(info.context)
    if not requester.has_perms(required_permission):
        raise PermissionDenied()

    return resolve_metadata(root.private_metadata)
