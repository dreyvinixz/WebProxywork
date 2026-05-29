from dataclasses import dataclass

import requests


USER_AGENT = "SI2-Content-Proxy/1.0"
TIMEOUT_SECONDS = 8


@dataclass(frozen=True)
class OriginResponse:
    status_code: int
    content_type: str
    body: bytes
    text: str
    encoding: str


def fetch_origin(url: str) -> OriginResponse:
    response = requests.get(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Encoding": "identity",
        },
        timeout=TIMEOUT_SECONDS,
        allow_redirects=True,
    )

    encoding = response.encoding or "utf-8"
    return OriginResponse(
        status_code=response.status_code,
        content_type=response.headers.get("Content-Type", "application/octet-stream"),
        body=response.content,
        text=response.text,
        encoding=encoding,
    )
