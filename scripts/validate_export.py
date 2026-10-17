#!/usr/bin/env python3
"""Check curated export inventory, file hashes and explicit exclusions."""
import hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
m=json.loads((root/'export-manifest.json').read_text())
errors=[]
for item in m['files']:
 p=root/item['path']
 if not p.is_file():errors.append('missing:'+item['path']);continue
 if hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:errors.append('hash:'+item['path'])
for p in root.rglob('*'):
 if not p.is_file() or '.git' in p.parts or '__pycache__' in p.parts:continue
 if p.suffix in {'.mp4','.m3u8','.ts','.mp3','.wav','.srt','.vtt','.pem','.key'}:errors.append('excluded-type:'+str(p.relative_to(root)))
print(json.dumps({'ok':not errors,'curated_card_counts':m['curated_counts'],'checked_files':len(m['files']),'errors':errors},ensure_ascii=False,indent=2))
sys.exit(bool(errors))
