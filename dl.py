#!/usr/bin/env python3
"""Resolve e baixa arquivos de bzzhr.to / buzzheavier.com / fuckingfast."""
import re, sys, os
from curl_cffi import requests as cr   # TLS fingerprint de Chrome -> passa Cloudflare

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://bzzhr.to/",
}

def resolve(url: str):
    """Retorna (link_direto, nome_do_arquivo) ou lança erro."""
    s = cr.Session(impersonate="chrome")          # <- chave do bypass
    r = s.get(url, headers=HEADERS, timeout=40)
    if r.status_code == 403:
        raise RuntimeError("Cloudflare ainda bloqueando (challenge interativo). "
                           "Veja a nota no final.")
    r.raise_for_status()
    html = r.text

    # 1) link direto explícito no botão de download
    m = re.search(r'href=["\']([^"\']*/d/[^"\']+)["\']', html) or \
        re.search(r'(https?://[^"\']+/d/[^"\']+\?[^"\']+)', html)
    # 2) fallback: qualquer URL de download com token
    if not m:
        m = re.search(r'(https?://[^"\']+\.(?:zip|rar|7z|iso|exe|mp4|mkv|pdf)[^"\']*)', html)
    if not m:
        raise RuntimeError("Link direto não encontrado na página (formato mudou?).")
    direct = m.group(1).replace("&amp;", "&")

    # nome do arquivo: Content-Disposition ou <title>
    fn = None
    cd = r.headers.get("Content-Disposition", "")
    m2 = re.search(r'filename="?([^";]+)', cd)
    if m2:
        fn = m2.group(1)
    if not fn:
        m3 = re.search(r'<title>([^<]+)</title>', html)
        fn = m3.group(1).strip() if m3 else "download.bin"
    return direct, fn

def download(url: str, out_dir: str = "."):
    direct, name = resolve(url)
    print(f"[+] Nome : {name}")
    print(f"[+] Link : {direct}")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)

    s = cr.Session(impersonate="chrome")
    with s.get(direct, headers=HEADERS, stream=True, timeout=60) as r:
        total = int(r.headers.get("Content-Length", 0))
        done = 0
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
                done += len(chunk)
                pct = done / total * 100 if total else 0
                print(f"\r    {done/1e6:.1f} MB / {total/1e6:.1f} MB ({pct:.0f}%)",
                      end="", flush=True)
    print(f"\n[✓] Salvo em: {path}")
    return path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python dl.py <link_bzzhr> [pasta_destino]")
        sys.exit(1)
    dest = sys.argv[2] if len(sys.argv) > 2 else "."
    download(sys.argv[1], dest)
