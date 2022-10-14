import graphene

from ..core.types import SortInputObjectType


class postSortField(graphene.Enum):
    TITLE = ["title", "slug"]
    SLUG = ["slug"]
    VISIBILITY = ["is_published", "title", "slug"]
    CREATION_DATE = ["created_at", "title", "slug"]
    ORDER_DATE = ["order_date", "title", "slug"]
    PUBLICATION_DATE = ["publication_date", "title", "slug"]

    @property
    def description(self):
        if self.name in postSortField.__enum__._member_names_:
            sort_name = self.name.lower().replace("_", " ")
            return f"Sort posts by {sort_name}."
        raise ValueError("Unsupported enum value: %s" % self.value)


class PostSortingInput(SortInputObjectType):
    class Meta:
        sort_enum = postSortField
        type_name = "posts"
