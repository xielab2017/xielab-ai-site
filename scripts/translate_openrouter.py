#!/usr/bin/env python3
import os,json,requests,time
from common import load,save
key=os.getenv('OPENROUTER_API_KEY'); model=os.getenv('OPENROUTER_MODEL','').strip() or 'openai/gpt-4.1-mini'
if not key: print('Translation skipped: OPENROUTER_API_KEY missing'); raise SystemExit
URL='https://openrouter.ai/api/v1/chat/completions'; headers={'Authorization':f'Bearer {key}','Content-Type':'application/json','HTTP-Referer':'https://www.xielab.net/','X-Title':'Xie Lab Website Sync'}
def ask(text,target):
    prompt=f"Translate the following scientific website text into {target}. Preserve gene symbols, strain names, abbreviations, DOI and patent numbers. Use concise professional academic language. Return only the translation.\\n\\n{text}"
    r=requests.post(URL,headers=headers,json={'model':model,'messages':[{'role':'user','content':prompt}],'temperature':0.1},timeout=120); r.raise_for_status(); return r.json()['choices'][0]['message']['content'].strip()
def process(file, fields):
    data=load(file); changed=0
    for x in data:
        for en,zh in fields:
            if x.get(en) and not x.get(zh): x[zh]=ask(x[en],'Simplified Chinese'); changed+=1; time.sleep(.4)
            elif x.get(zh) and not x.get(en): x[en]=ask(x[zh],'American English'); changed+=1; time.sleep(.4)
    save(file,data); print(file,changed)
process('publications.json',[('title','title_zh'),('abstract_en','abstract_zh')])
process('patents.json',[('title_en','title_zh'),('abstract_en','abstract_zh')])
process('news.json',[('title_en','title_zh'),('body_en','body_zh')])
