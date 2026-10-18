# debug.py  ->  python debug.py https://bzzhr.to/e3r5uyh44ptv
import sys, re, json
from curl_cffi import requests as cr

url = sys.argv[1]
s = cr.Session(impersonate="chrome")

try:
    r = s.get(url, timeout=40, allow_redirects=True)
    print("STATUS", r.status_code, "| FINAL:", r.url, "| LEN", len(r.text))
    print("CT:", r.headers.get("content-type"))
    print("COOKIES:", dict(s.cookies))
    print("=" * 70)
    print(r.text[:6000])
    print("=" * 70)

    for pat in [r'"(/api/[^"]+)"', r'"(/[a-z0-9_]+/download[^"]+)"',
                r'data-url="([^"]+)"', r'(https?://[^"\']+/d/[^"\']+)',
                r'"(downloadUrl|download_url|fileUrl|file_url)"']:
        hits = re.findall(pat, r.text)
        if hits:
            print(pat, "->", sorted(set(hits))[:10])
except Exception as e:
    print("ERRO na pagina:", repr(e))

fid = url.rstrip("/").split("/")[-1]
root = "/".join(url.split("/")[:3])
for cand in [f"{root}/{fid}.json",
             f"{root}/api/v1/file/{fid}.json",
             f"{root}/api/v1/files/{fid}.json",
             f"{root}/download/{fid}"]:
    try:
        q = s.get(cand, headers={"Accept": "application/json", "Referer": url}, timeout=30)
        print(q.status_code, cand, "->", q.text[:300].replace("\n", " "))
    except Exception as e:
        print("ERR", cand, repr(e)[:120])
