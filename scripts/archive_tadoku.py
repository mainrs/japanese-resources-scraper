#!/usr/bin/env python3

import hashlib
import json
import shutil
import sys
from itertools import groupby
from pathlib import Path
from typing import Tuple

from scrapy import cmdline

allowed_licenses = ["CC-BY-NC-ND-4.0"]


def main():
    crawler = sys.argv[1]
    run_crawler(crawler)
    create_archive(crawler)


def create_archive(crawler: str):
    crawler_dir = Path(f"./data/archive/{crawler}")
    crawler_dir.mkdir(exist_ok=True, parents=True)
    data_file = Path(f"./data/{crawler}.json")

    with data_file.open("r") as f:
        books = json.load(f)
        print(f"Crawled books: {len(books)}")

        # We filter all books to only include licenses that allow us to share the files.
        # We then group the books by their level, creating 6 lists of books with the
        # same level.
        books = list(filter(lambda x: x['license']['spdx'] in allowed_licenses, books))
        print(f"Permissible license: {len(books)}")
        books.sort(key=lambda x: x['level'])
        books = groupby(books, key=lambda x: x['level'])

        files_directory = Path(f"./data/files/full")
        images_directory = Path(f"./data/images/full")

        # We also copy over the raw JSON data of all available books, even those
        # with non-permissible licenses. This adds the possibility to validate
        # the uploaded data.
        data_file_dest = crawler_dir.joinpath("data.json")
        shutil.copy(data_file, data_file_dest)

        # Every level gets its own folder. Files are named after the book's title.
        for (level, grouped_books) in books:
            directory = Path(f"./data/archive/{crawler}/{level}")
            directory.mkdir(exist_ok=True, parents=True)

            for book in grouped_books:
                title = merge_title(book['title'])
                cover_filename, cover_extension = to_hashed_filename(book['cover_url'])
                cover_file = images_directory.joinpath(cover_filename)
                pdf_filename, pdf_extension = to_hashed_filename(book['pdf_url'])
                pdf_file = files_directory.joinpath(pdf_filename)

                cover_file_dest = directory.joinpath(f"{title}.{cover_extension}")
                pdf_file_dest = directory.joinpath(f"{title}.pdf")
                shutil.copy(cover_file, cover_file_dest)
                shutil.copy(pdf_file, pdf_file_dest)

                # Audio and Print URLs are not always available.
                if book['audio_url'] is not None:
                    audio_filename, audio_extension = to_hashed_filename(book['audio_url'])
                    audio_file = files_directory.joinpath(audio_filename)
                    audio_file_dest = directory.joinpath(f"{title}.{audio_extension}")
                    shutil.copy(audio_file, audio_file_dest)
                if book['pdf_print_url'] is not None:
                    audio_filename, audio_extension = to_hashed_filename(book['pdf_print_url'])
                    audio_file = files_directory.joinpath(audio_filename)
                    audio_file_dest = directory.joinpath(f"{title}_print.{audio_extension}")
                    shutil.copy(audio_file, audio_file_dest)

    print("Done")


def run_crawler(name: str):
    directory = Path(f"./data")
    directory.mkdir(exist_ok=True)
    json_file = directory.joinpath(f"{name}.json")

    cmdline.execute(f"scrapy crawl {name} -o {json_file}".split())


def to_hashed_filename(url: str) -> Tuple[str, str]:
    extension = url.rsplit('.', maxsplit=1)[-1]
    return f"{to_sha1(url)}.{extension}", extension


def to_sha1(s: str) -> str:
    sha1 = hashlib.sha1()
    sha1.update(s.encode('utf-8'))
    return sha1.hexdigest()


def split_filename(s: str) -> Tuple[str, str]:
    values = s.rsplit(".", maxsplit=1)
    return values[0], values[1]


def merge_title(rubies) -> str:
    return "".join([ruby['text'] for ruby in rubies])


if __name__ == '__main__':
    main()
