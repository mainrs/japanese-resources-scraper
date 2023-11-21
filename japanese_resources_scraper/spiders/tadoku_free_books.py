from typing import Any
from urllib.parse import urlparse
from scrapy import Request, Spider
from scrapy.http import Response
from japanese_resources_scraper.items import ScrapedTadokuBook


class TadokuFreeBooksSpider(Spider):
    name = "tadoku_free_books"
    allowed_domains = ["tadoku.org"]
    start_urls = ["https://tadoku.org/japanese/en/free-books-en"]

    def parse(self, response: Response, **kwargs: Any):
        book_urls = response.xpath("//div[@class = 'bl-thumb']/a[contains(@href, '/book/')]/@href").getall()
        for book_url in book_urls:
            yield Request(book_url, callback=_parse_book)


def _parse_book(response: Response) -> Any:
    url = response.url
    book_id = urlparse(url).path.rstrip('/').rpartition('/')[2]

    title_fragments = response.xpath("//div[@class = 'bd-title']/h1/node()").getall()
    title = "".join(title_fragments)
    description_fragments = response.xpath("//div[@class = 'bd-desc-jp']/p/node()").getall()
    description = "".join(description_fragments)

    level = response.xpath("//div[contains(@class, 'bd-detail-wrap')]//a[contains(@href, 'level=')]/text()").get()
    rating = response.xpath("//div[@class = 'tdk-star-rating-container']/@data-rating").get()

    license_elem = response.xpath("//div[@class = 'bd-note']//span[@class = 'bd-en']//*[contains(., 'licensed')]/a")
    license_url = license_elem.xpath("@href").get()
    license_name = license_elem.xpath("text()").get()

    cover_url = response.xpath("//div[@class = 'bd-thumb']/img/@src").get()
    pdf_url = response.xpath("//div[@class = 'bd-lookinside-pdf']/ul/li/a[span[text() = '｜PDF']]/@href").get()
    pdf_print_url = response.xpath(
        "//div[@class = 'bd-lookinside-pdf']/ul/li/a[span[text() = '｜PDF for print']]/@href").get()
    audio_url = response.xpath("//div[@class = 'bd-lookinside-pdf']/ul/li/a[span[text() = '｜MP3']]/@href").get()

    item = ScrapedTadokuBook(
        id=book_id,
        title=title,
        description=description,
        level=level,
        rating=rating,
        license_name=license_name,
        license_url=license_url,
        audio_url=audio_url,
        cover_url=cover_url,
        pdf_print_url=pdf_print_url,
        pdf_url=pdf_url,
        url=url,
        file_urls=[],
        image_urls=[],
    )

    # Configure all PDF files to be downloaded by the pipeline.
    item['file_urls'].append(pdf_url)
    if pdf_print_url is not None:
        item['file_urls'].append(pdf_print_url)
    if cover_url is not None:
        item['image_urls'].append(cover_url)

    if audio_url is not None:
        yield Request(audio_url, callback=_finish_parse, meta={"item": item}, dont_filter=True)
    else:
        yield item


def _finish_parse(response: Response) -> Any:
    item = response.meta.get("item")
    audio_url = urlparse(item['audio_url'])
    post_id = audio_url.fragment

    audio_url = response.xpath(
        f"//tr[td/div[@id = '{post_id}']]/td[@class = 'audiodownload-download']/ul/li/a/@href").get()

    item['audio_url'] = audio_url
    if audio_url is not None:
        item['file_urls'].append(audio_url)
    yield item
