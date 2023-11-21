from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List

from lxml.etree import Element
from scrapy import Selector


@dataclass
class RubyText:
    text: str
    reading: Optional[str] = None

    @staticmethod
    def with_reading(text: str, reading: str) -> RubyText:
        return RubyText(text=text, reading=reading)

    @staticmethod
    def without_reading(text: str) -> RubyText:
        return RubyText(text=text)

    @staticmethod
    def from_selector(selector: Selector) -> RubyText:
        text: Optional[str] = None
        reading: Optional[str] = None

        for node in selector.xpath("text() | *"):
            tag = node.xpath("name()").get()

            # Skip legacy ruby tags.
            if tag == 'rp':
                continue

            if tag == 'rt':
                reading = node.xpath("text()").get()
            elif tag:
                text = node.xpath("text()").get()
            else:
                text = node.get()

        return RubyText(text=text, reading=reading)


def process_ruby_selector(selector: Selector) -> List[RubyText]:
    nodes = selector.xpath("node()")
    result = []

    for node in nodes:
        root: Element | str = node.root

        if isinstance(root, str):
            # Edge case `<br>`
            if root != "<br>":
                result.append(RubyText.without_reading(root))
            continue

        if root.tag == 'ruby':
            result.append(RubyText.from_selector(node))
            continue

    return result
