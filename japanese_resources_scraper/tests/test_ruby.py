from scrapy import Selector

from japanese_resources_scraper.utils.ruby import process_ruby_selector, RubyText


def test_ruby_no_fallback():
    text = "チワワの<ruby>花<rt>はな</rt></ruby>すけ～お<ruby>花見<rt>はなみ</rt></ruby>"
    selector = Selector(text=text)
    ruby = process_ruby_selector(selector.xpath("//p")[0])

    expected = [
        RubyText(text="チワワの"),
        RubyText(text="花", reading="はな"),
        RubyText(text="すけ～お"),
        RubyText(text="花見", reading="はなみ"),
    ]
    assert ruby == expected

def test_ruby_with_fallback():
    text = "チワワの<ruby>花<rp>(</rp><rt>はな</rt><rp>)</rp></ruby>すけ～お<ruby>花見<rt>はなみ</rt></ruby>"
    selector = Selector(text=text)
    ruby = process_ruby_selector(selector.xpath("//p")[0])

    expected = [
        RubyText(text="チワワの"),
        RubyText(text="花", reading="はな"),
        RubyText(text="すけ～お"),
        RubyText(text="花見", reading="はなみ"),
    ]
    assert ruby == expected
