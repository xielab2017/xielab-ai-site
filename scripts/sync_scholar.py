#!/usr/bin/env python3
"""Optional Google Scholar merge. Google Scholar has no official public API.
This adapter uses a configured third-party provider and is disabled unless credentials are present.
"""
import os, requests
from common import load,save,merge_records,norm_doi
provider=os.getenv('SCHOLAR_PROVIDER','').lower(); key=os.getenv('SERPAPI_API_KEY',''); author=os.getenv('SCHOLAR_AUTHOR_ID','') or load('site.json').get('scholar_author_id','')
if provider!='serpapi' or not key or not author:
    print('Scholar sync skipped: configure SCHOLAR_PROVIDER=serpapi, SERPAPI_API_KEY and SCHOLAR_AUTHOR_ID'); raise SystemExit
r=requests.get('https://serpapi.com/search.json',params={'engine':'google_scholar_author','author_id':author,'api_key':key,'num':100},timeout=90); r.raise_for_status(); data=r.json(); out=[]
for x in data.get('articles',[]):
    out.append({'title':x.get('title',''),'authors':x.get('authors',''),'journal':x.get('publication',''),'year':int(x.get('year') or 0),'doi':norm_doi(x.get('doi','')),'scholar_citations':(x.get('cited_by') or {}).get('value',0),'scholar_url':x.get('link',''),'source':['google-scholar']})
save('publications.json',merge_records(load('publications.json'),out)); print(f'Merged {len(out)} Scholar records')
