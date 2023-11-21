from dataclasses import dataclass
from typing import List
from scrapy import Field, Item
from japanese_resources_scraper.utils.license import License
from japanese_resources_scraper.utils.ruby import RubyText


class ScrapedTadokuBook(Item):
    id = Field()
    title = Field()
    description = Field()
    level = Field()
    rating = Field()
    license_name = Field()
    license_url = Field()

    url = Field()
    audio_url = Field()
    cover_url = Field()
    pdf_print_url = Field()
    pdf_url = Field()

    # Automatically downloaded by standard `scrapy` pipeline.
    file_urls = Field()
    image_urls = Field()


@dataclass
class FreeTadokuBook:
    id: int
    title: List[RubyText]
    description: List[RubyText]

    level: int
    license: License
    rating: float

    audio_url: str
    cover_url: str
    pdf_print_url: str
    pdf_url: str
    url: str
