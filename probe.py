"""Verifica URLs de download e seus redirecionamentos.

Uso: python probe.py https://exemplo.com/arquivo
"""

import argparse
from urllib.parse import urlparse

try:
    from curl_cffi import requests
except ImportError as error:
    raise SystemExit("Dependência ausente: instale com 'pip install curl-cffi'.") from error

HOSTS_ESPERADOS = ("bzzhr", "buzzheavier")
REDIRECT_CODES = (301, 302, 303, 307, 308)


def validar_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("a URL precisa começar com http:// ou https://")


def verificar(session, url: str, timeout: float) -> str:
    validar_url(url)
    response = session.get(url, allow_redirects=False, timeout=timeout)
    location = response.headers.get("location", "")
    if response.status_code in REDIRECT_CODES:
        destino = urlparse(location).netloc.lower()
        verdict = (
            "MORTO (redirecionamento externo)"
            if destino and not any(host in destino for host in HOSTS_ESPERADOS)
            else "redirecionamento interno"
        )
    elif response.status_code == 404:
        verdict = "MORTO (404)"
    elif response.status_code == 200:
        verdict = "VIVO"
    else:
        verdict = f"INUSUAL ({response.status_code})"
    suffix = f" -> {location}" if location else ""
    return f"{response.status_code:3}  {verdict:32} {url}{suffix}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verifica links de download.")
    parser.add_argument("urls", nargs="+", help="uma ou mais URLs para verificar")
    parser.add_argument("--timeout", type=float, default=40, help="timeout em segundos")
    args = parser.parse_args()
    with requests.Session(impersonate="chrome") as session:
        for url in args.urls:
            try:
                print(verificar(session, url, args.timeout))
            except ValueError as error:
                print(f"ERRO  {url}: {error}")
            except requests.RequestException as error:
                print(f"ERRO  {url}: falha de rede ({type(error).__name__})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
