import graphene

from ...core.culture import Cultures
from ...core.post_types import PostTypes
from ..core.enums import to_enum

CultureEnum = to_enum(Cultures)
PostTypeEnum = to_enum(PostTypes)

