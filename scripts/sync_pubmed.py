#!/usr/bin/env python3
import os, requests, xml.etree.ElementTree as ET
from common import load,save,merge_records,norm_doi
BASE='https://eutils.ncbi.nlm.nih.gov/entrez/eutils'
site=load('site.json'); old=load('publications.json'); api=os.getenv('NCBI_API_KEY','')
params={'db':'pubmed','retmode':'json','retmax':500,'term':' OR '.join(f'({q})' for q in site.get('pubmed_queries',[]))}
if api: params['api_key']=api
ids=requests.get(BASE+'/esearch.fcgi',params=params,timeout=60).json()['esearchresult']['idlist']
if not ids: print('No PubMed records'); raise SystemExit
p={'db':'pubmed','retmode':'xml','id':','.join(ids)}
if api:p['api_key']=api
root=ET.fromstring(requests.get(BASE+'/efetch.fcgi',params=p,timeout=90).text)
out=[]
for a in root.findall('.//PubmedArticle'):
    mc=a.find('.//MedlineCitation'); art=a.find('.//Article');
    if mc is None or art is None: continue
    pmid=(mc.findtext('PMID') or '').strip(); title=''.join(art.find('ArticleTitle').itertext()) if art.find('ArticleTitle') is not None else ''
    authors=[]
    for au in art.findall('.//Author'):
        n=' '.join(filter(None,[au.findtext('ForeName'),au.findtext('LastName')])).strip()
        if n: authors.append(n)
    journal=art.findtext('.//Journal/Title') or ''
    year=art.findtext('.//JournalIssue/PubDate/Year') or art.findtext('.//ArticleDate/Year') or '0'
    abstract=' '.join(''.join(x.itertext()) for x in art.findall('.//Abstract/AbstractText'))
    doi=''
    for eid in a.findall('.//ArticleId'):
        if eid.attrib.get('IdType')=='doi': doi=norm_doi(eid.text); break
    out.append({'title':title,'authors':', '.join(authors),'journal':journal,'year':int(year) if str(year).isdigit() else 0,'doi':doi,'pmid':pmid,'abstract_en':abstract,'abstract_zh':'','scholar_citations':0,'source':['pubmed']})
save('publications.json',merge_records(old,out)); print(f'Synced {len(out)} PubMed records')
