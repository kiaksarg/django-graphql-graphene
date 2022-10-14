from collections import defaultdict
from promise import Promise

from ..core.dataloaders import DataLoader
from ...post import models


class ChildrenByIdLoader(DataLoader):
    context_key = "children_by_id"

    def batch_load_fn(self, keys):
        post_in_posts = models.Postcat.objects.filter(parent_id__in=keys).order_by('sort_order')

        items_map = defaultdict(list)

        for post_in_post in post_in_posts:
            items_map[post_in_post.parent_id].append(post_in_post)

        return Promise.resolve(
            [items_map[post_item_id] for post_item_id in keys]
        )

class ChildByIdLoader(DataLoader):
    context_key = "child_by_id"

    def batch_load_fn(self, keys):
        posts = models.Post.objects.in_bulk(keys)
        return Promise.resolve(
           [posts.get(post_id) for post_id in keys]
        )

