#!/usr/bin/env python3
"""Verify the built offline package, provenance hashes, links, and embedded trial counts."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

SITE=Path(__file__).resolve().parents[1]
ROOT=SITE.parent
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.dependencies=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'): self.ids.add(a['id'])
        if tag=='a' and a.get('href'): self.links.append(a['href'])
        if tag in ('script','img','iframe','source','video','audio') and a.get('src'):self.dependencies.append(a['src'])
        if tag=='link' and a.get('href'):self.dependencies.append(a['href'])

def verify():
    manifest=json.loads((SITE/'build-manifest.json').read_text());pages={}
    for relative,digest in manifest['sources'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,f'Stale source: {relative}'
    for name,digest in manifest['pages'].items():
        raw=(SITE/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==digest,f'Output edited: {name}'
        text=raw.decode();parser=Page();parser.feed(text);pages[name]=parser
        assert not parser.dependencies,(name,parser.dependencies)
        assert not re.search(r'\bfetch\s*\(|@import\s',text),name
        assert '/home/' not in text and '/tmp/' not in text,name
        payload=json.loads(re.search(r'<script type="application/json" id="dataset">(.*?)</script>',text,re.S)[1])
        for exp,data in payload.get('experiments',{}).items():
            assert sum(c['n'] for c in data['cells'])==manifest['trials'][exp]
            assert sum(g['n'] for g in data['routes'])==manifest['trials'][exp]
            for c in data['cells']:
                groups=[g for g in data['routes'] if (g['model'],g['graph'],g['variant'])==(c['model'],c['graph'],c['variant'])]
                assert c['n']==sum(g['n'] for g in groups)==30
                assert c['correct']==sum(o['correct'] for g in groups for o in g['outcomes'])
                assert c['goal']==sum(o['goal'] for g in groups for o in g['outcomes'])
                assert 0<=c['correct']<=c['goal']<=c['n']
    for name,parser in pages.items():
        for href in parser.links:
            assert not href.startswith(('http:','https:','//')),href
            path,_,anchor=href.partition('#');target=path.split('?')[0] or name
            assert target in pages,(name,href)
            if anchor:assert anchor in pages[target].ids,(name,href)
    print(f'PASS: {len(pages)} pages; local links, inline assets, source hashes, and every embedded condition count/correctness/Goal count.')
if __name__=='__main__':verify()
