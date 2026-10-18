# probe.py - python probe.py https//bzzhr.toe3r5uyh44ptv
import sys
from curl_cffi import requests as cr

s = cr.Session(impersonate=chrome)
for url in sys.argv[1]
    r = s.get(url, allow_redirects=False, timeout=40)
    loc = r.headers.get(location, )
    if r.status_code in (301, 302, 303, 307, 308)
        verdict = MORTO (redirect pra fora) if bzzhr not in loc and buzzheavier not in loc else redirecionamento interno
    elif r.status_code == 404
        verdict = MORTO (404)
    elif r.status_code == 200
        verdict = VIVO
    else
        verdict = finusual ({r.status_code})
    print(f{r.status_code3}  {verdict28} {url} + (f  - {loc} if loc else ))
