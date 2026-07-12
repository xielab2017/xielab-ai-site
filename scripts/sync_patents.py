#!/usr/bin/env python3
"""Discover patent records from Google Patents public search pages.
The parser is deliberately conservative; manual records are retained when the upstream layout changes.
"""
import os,re,requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus,urljoin
from common import load,save,merge_records
site=load('site.json'); old=load('patents.json'); out=[]
headers={'User-Agent':'XieLabWebsite/1.0 (+https://www.xielab.net/)'}
for name in site.get('patent_inventor_names',[]):
    url='https://patents.google.com/?inventor='+quote_plus(name)
    try:
        h=requests.get(url,headers=headers,timeout=45); h.raise_for_status(); soup=BeautifulSoup(h.text,'html.parser')
        for item in soup.select('search-result-item, article, .result'):
            a=item.select_one('a[href*="/patent/"]'); title=item.select_one('.result-title, h3, h4')
            if not a or not title: continue
            text=' '.join(item.get_text(' ',strip=True).split()); num=''
            m=re.search(r'\b(?:CN|US|WO|EP)\s?\d+[A-Z]\d?\b',text); num=m.group(0).replace(' ','') if m else ''
            out.append({'title_en':title.get_text(' ',strip=True),'title_zh':'','inventors':name,'publication_number':num,'date':'','abstract_en':'','abstract_zh':'','url':urljoin('https://patents.google.com',a.get('href')),'source':['google-patents']})
    except Exception as e: print('Patent source warning:',name,e)
# patent-specific dedupe
seen={}
for p in old+out:
    k=p.get('publication_number') or p.get('url') or re.sub(r'\W+','',p.get('title_en','').lower())
    if k: seen[k]={**seen.get(k,{}),**p}
save('patents.json',list(seen.values())); print(f'Discovered {len(out)} patent candidates; total {len(seen)}')
