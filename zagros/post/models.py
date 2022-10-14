from django.db import models
from django.utils import timezone
from draftjs_sanitizer import clean_draft_js
# from tinymce import models as tinymce_models

from ..core.db.fields import SanitizedJSONField
from ..core.models import ModelWithMetadata, SeoModel
from ..core.permissions import PostPermissions
from ..account.models import User
from ..core.culture import Cultures
from ..core.post_types import PostTypes
# from ..core.models import PublishableModel, PublishedQuerySet


class Post(SeoModel, ModelWithMetadata):
    name = models.CharField(max_length=250, blank=True)
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=750)
    parent_self = models.ForeignKey(
        "self", null=True, blank=True, related_name="children_self", on_delete=models.CASCADE
    )
    post_content = models.TextField(blank=True)
    post_content_json = SanitizedJSONField(
        blank=True, default=dict, sanitizer=clean_draft_js
    )
    description = models.CharField(max_length=450, blank=True)
    mim_type = models.CharField(max_length=100, blank=True)
    post_type = models.CharField(
        max_length=15, db_index=True, choices=PostTypes.CHOICES, default=PostTypes.POST)
    author = models.ForeignKey(
        User, blank=True, null=True, related_name="posts", on_delete=models.SET_NULL)
    author_text = models.CharField(max_length=250, blank=True)
    culture = models.CharField(
        max_length=10, db_index=True, choices=Cultures.CHOICES, default=Cultures.PERSIAN)

    order_date = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ("-order_date",)
        permissions = ((PostPermissions.MANAGE_POSTS.codename, "Manage posts."),)

    def __str__(self):
        return self.title

class Postcat(models.Model):
    child = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="parents")
    parent = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="children")
    sort_order = models.IntegerField(db_index=True, null=True)
    class Meta:
        permissions = ((PostPermissions.MANAGE_CATS.codename, "Manage cats."),)
