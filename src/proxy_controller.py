from dataclasses import dataclass
from urllib.parse import urlparse

from flask import Blueprint, Response, request
from requests import RequestException

from src.access_audit import AccessAudit
from src.content_policy import ContentPolicy
from src.html_pages import blocked_page, error_page
from src.origin_client import fetch_origin
from src.text_rewriter import TextRewriter


proxy_blueprint = Blueprint("proxy", __name__)
policy = ContentPolicy()
rewriter = TextRewriter()
audit = AccessAudit()


@dataclass(frozen=True)
class ParsedTarget:
    url: str
    domain: str


LOCAL_HOSTS = {"127.0.0.1", "localhost", "0.0.0.0"}


def parse_target(raw_target: str, query_string: str = "") -> ParsedTarget:
    target = (raw_target or "").strip()
    if not target:
        raise ValueError("URL vazia.")

    query_string = (query_string or "").strip()
    if query_string and "?" not in target:
        target = f"{target}?{query_string}"

    if "://" not in target:
        target = f"http://{target}"

    parsed = urlparse(target)
    if parsed.scheme != "http":
        raise ValueError("Este proxy aceita apenas URLs HTTP.")
    if not parsed.netloc:
        raise ValueError("URL sem dominio de destino.")

    return ParsedTarget(url=target, domain=parsed.hostname or parsed.netloc)


def build_target_from_request(route_target: str, host_header: str, server_port: str, query_string: str = "") -> str:
    route_target = (route_target or "").strip()
    host_header = (host_header or "").strip()
    server_port = str(server_port or "").strip()

    if _looks_like_proxy_request(route_target, host_header, server_port):
        path = f"/{route_target}" if route_target else ""
        return f"http://{host_header}{path}"

    if route_target and query_string and "?" not in route_target:
        return f"{route_target}?{query_string}"
    return route_target


def build_target_from_environ(route_target: str, environ: dict, query_string: str = "") -> str:
    raw_uri = (environ.get("RAW_URI") or environ.get("REQUEST_URI") or "").strip()
    if raw_uri.startswith("http://"):
        return raw_uri

    return build_target_from_request(
        route_target,
        environ.get("HTTP_HOST", ""),
        environ.get("SERVER_PORT", "5000"),
        query_string,
    )


def _looks_like_proxy_request(route_target: str, host_header: str, server_port: str) -> bool:
    if "://" in route_target:
        return False

    host_without_port = host_header.split(":", 1)[0].lower()
    if host_without_port in LOCAL_HOSTS:
        return False

    return not host_header.endswith(f":{server_port}")


@proxy_blueprint.route("/", methods=["GET", "HEAD"])
def index() -> Response:
    request_target = build_target_from_environ(
        "",
        request.environ,
        request.query_string.decode("utf-8", errors="ignore"),
    )
    if request_target:
        return proxy_request("")

    body = (
        "<!doctype html><html lang='pt-BR'><meta charset='utf-8'>"
        "<title>SI2 Content Proxy</title>"
        "<body style='font-family:Arial,sans-serif;margin:40px'>"
        "<h1>SI2 Content Proxy</h1>"
        "<p>Informe uma URL depois da barra.</p>"
        "<code>http://localhost:5000/http://neverssl.com</code>"
        "</body></html>"
    )
    return Response(body, status=200, content_type="text/html; charset=utf-8")


@proxy_blueprint.route("/<path:target>", methods=["GET", "HEAD"])
def proxy_request(target: str) -> Response:
    query_string = request.query_string.decode("utf-8", errors="ignore")
    request_target = build_target_from_environ(
        target,
        request.environ,
        query_string,
    )

    try:
        parsed = parse_target(request_target, query_string)
    except ValueError as exc:
        return Response(error_page("Requisicao invalida", str(exc)), status=400, content_type="text/html; charset=utf-8")

    if policy.is_blocked(parsed.domain):
        audit.record(parsed.url, parsed.domain, "blocked", 403, 0)
        return Response(blocked_page(parsed.domain), status=403, content_type="text/html; charset=utf-8")

    try:
        origin = fetch_origin(parsed.url)
    except RequestException as exc:
        audit.record(parsed.url, parsed.domain, "error", 502, 0)
        return Response(error_page("Falha ao acessar origem", str(exc)), status=502, content_type="text/html; charset=utf-8")

    content_type = origin.content_type
    body = origin.body
    filtered_count = 0
    action = "allowed"

    if "text/html" in content_type.lower():
        rewritten, filtered_count = rewriter.rewrite(origin.text)
        if filtered_count:
            action = "filtered"
        body = rewritten.encode(origin.encoding or "utf-8", errors="replace")
        content_type = _with_charset(content_type, origin.encoding or "utf-8")

    audit.record(parsed.url, parsed.domain, action, origin.status_code, filtered_count)
    return Response(body, status=origin.status_code, content_type=content_type)


def _with_charset(content_type: str, encoding: str) -> str:
    if "charset=" in content_type.lower():
        return content_type
    return f"{content_type}; charset={encoding}"
