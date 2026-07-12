#!/usr/bin/env python3
"""Archive the legacy xielab.net pages and assets for migration review.
Run from a network that can access the legacy host. It never overwrites structured data automatically.
"""
import argparse,re,requests,json
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse
ap=argparse.ArgumentParser(); ap.add_argument('--base',default='http://www.xielab.net/'); ap.add_argument('--max-pages',type=int,default=200); args=ap.parse_args()
out=Path(__file__).resolve().parents[1]/'legacy_archive'; out.mkdir(exist_ok=True)
q=[args.base]; seen=set(); manifest=[]; session=requests.Session(); session.headers['User-Agent']='Mozilla/5.0 XieLabMigration/1.0'
while q and len(seen)<args.max_pages:
    u=q.pop(0)
    if u in seen: continue
    try:r=session.get(u,timeout=30);r.raise_for_status()
    except Exception as e: print('skip',u,e); continue
    seen.add(u); ct=r.headers.get('content-type',''); path=urlparse(u).path.strip('/') or 'index.html'; path=path if Path(path).suffix else path+'.html'; dest=out/path; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(r.content); manifest.append({'url':u,'file':str(dest.relative_to(out)),'content_type':ct})
    if 'text/html' in ct:
        soup=BeautifulSoup(r.text,'html.parser')
        for tag,attr in [('a','href'),('img','src'),('script','src'),('link','href')]:
            for el in soup.find_all(tag):
                v=el.get(attr)
                if not v: continue
                x=urljoin(u,v); p=urlparse(x)
                if p.netloc==urlparse(args.base).netloc and x not in seen:
                    if tag=='a' or re.search(r'\.(?:png|jpe?g|gif|svg|css|js|pdf)(?:$|\?)',p.path,re.I): q.append(x)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8'); print('Archived',len(manifest),'resources')
