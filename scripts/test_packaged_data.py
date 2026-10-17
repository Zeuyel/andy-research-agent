#!/usr/bin/env python3
"""Check all packaged cards are retrievable and have explicit excerpts."""
import importlib.util,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'skills/andy-research-agent/scripts/retrieve_knowledge.py'
spec=importlib.util.spec_from_file_location('retrieval',p)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
r=mod.search(root/'knowledge','科研 检索 写作 基金 证据',limit=30)
assert not r['source_errors'],r['source_errors']
expected={'method_rule':18,'topic_reading':43,'article_reading':27,'video_text':97}
assert r['available_card_counts']==expected,r['available_card_counts']
for kind,n in expected.items():
 c=r['source_coverage'][kind]
 assert c['explicit_evidence_cards']==n,(kind,c)
 assert c['suppressed_no_explicit_evidence']==0,(kind,c)
for q in ['先写前言还是结果讨论','基金选题最小验证','如何构建证据链']:
 x=mod.search(root/'knowledge',q,limit=3)
 assert x['result_count']>0,q
for p in (root/'knowledge').rglob('*'):
 if p.is_file():
  text=p.read_text()
  assert '/data/' not in text,str(p)
  assert 'full_text_sources' not in text,str(p)
  assert not any(z in text for z in ['BEGIN PRIVATE KEY','ghp_','github_pat_']),str(p)
print(json.dumps({'ok':True,'available_card_counts':expected,'every_packaged_card_has_explicit_evidence':True,'live_queries':3},ensure_ascii=False,indent=2))
