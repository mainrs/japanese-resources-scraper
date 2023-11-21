from dataclasses import dataclass
from typing import Optional


@dataclass
class License:
    spdx: str
    url: Optional[str] = None
