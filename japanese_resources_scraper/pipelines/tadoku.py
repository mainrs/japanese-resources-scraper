from typing import List, Optional
from urllib.parse import urlparse

from scrapy import Spider, Selector

from japanese_resources_scraper.items import ScrapedTadokuBook, FreeTadokuBook
from japanese_resources_scraper.utils.license import License
from japanese_resources_scraper.utils.ruby import RubyText, process_ruby_selector

licenses = {"CC BY-NC-ND 4.0": "CC-BY-NC-ND-4.0"}


class TadokuPipeline:
    def process_item(self, item, spider):
        return _process_tadoku_book(item, spider) if isinstance(item, ScrapedTadokuBook) else item


def _process_tadoku_book(item: ScrapedTadokuBook, spider: Spider):
    id = _process_id(item)
    license = _process_license(item)
    level = _process_level(item)
    rating = _process_rating(item)
    title = _process_ruby_fragments(item['title'])
    description = _process_ruby_fragments(item['description'])

    return FreeTadokuBook(
        id=id,
        title=title,
        description=description,
        license=license,
        level=level,
        rating=rating,
        audio_url=item['audio_url'],
        cover_url=item['cover_url'],
        pdf_print_url=item['pdf_print_url'],
        pdf_url=item['pdf_url'],
        url=item['url'],
    )


def _process_id(item: ScrapedTadokuBook) -> int:
    return int(item['id'])


def _process_level(item: ScrapedTadokuBook) -> int:
    level = item['level'].lower().lstrip("level").strip()
    return int(level)


def _process_license(item: ScrapedTadokuBook) -> License:
    return License(spdx=licenses[item['license_name']], url=item['license_url'])


def _process_rating(item: ScrapedTadokuBook) -> float:
    return float(item['rating'])


def _process_ruby_fragments(ruby: str) -> List[RubyText]:
    selector = Selector(text=ruby)

    # When re-wrapping the string into a `Selector`, the content sometimes gets wrapped in valid HTML.
    # We pre-select the correct sub-part of the selector before working on it.
    if ruby.startswith("<ruby>"):
        selector = selector.xpath("//html/body")
    elif ruby.startswith("<small>"):
        selector = selector.xpath("//small")
    else:
        selector = selector.xpath("//p")

    return process_ruby_selector(selector[0])
