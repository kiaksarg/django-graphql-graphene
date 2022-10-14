import django_filters

from ...post.models import Post
from ..core.types import FilterInputObjectType
from ..utils.filters import filter_by_query_param


def filter_post_search(qs, _, value):
    post_fields = ["post_content", "description", "title", "name"]
    qs = filter_by_query_param(qs, value, post_fields)
    return qs


class PostFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=filter_post_search)
    culture = django_filters.CharFilter(
        field_name='culture', lookup_expr='iexact')
    post_type = django_filters.CharFilter(
        field_name='post_type', lookup_expr='iexact')

    class Meta:
        model = Post
        fields = ["search", "culture", "post_type"]


class PostFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = PostFilter
