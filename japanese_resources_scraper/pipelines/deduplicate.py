from typing import Set

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class DeduplicatePipeline:
    seen_ids: Set[int | str] = set()

    def process_item(self, item, spider):
        item = ItemAdapter(item)
        if item['id'] in self.seen_ids:
            raise DropItem(f"{item['id']}")
        return item
