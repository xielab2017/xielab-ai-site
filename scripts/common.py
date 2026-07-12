from pathlib import Path
import json, re, time
ROOT=Path(__file__).resolve().parents[1]
def load(name): return json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))
def save(name,obj): (ROOT/'data'/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def norm_doi(x):
    x=(x or '').strip().lower(); x=re.sub(r'^https?://(dx\.)?doi\.org/','',x); return x

def merge_records(old,new):
    by={}
    for p in old+new:
        key=norm_doi(p.get('doi')) or str(p.get('pmid') or '') or re.sub(r'\W+','',p.get('title','').lower())
        if not key: continue
        by[key]={**by.get(key,{}),**{k:v for k,v in p.items() if v not in (None,'',[])}}
    return sorted(by.values(),key=lambda x:(x.get('year') or 0,x.get('title','')),reverse=True)
