import argparse,datetime,hashlib,json,time,urllib.request,urllib.error
from build_catalog import ROOT,validate
p=argparse.ArgumentParser();p.add_argument('--commit',required=True);p.add_argument('--sequence',type=int,required=True);args=p.parse_args()
raw=(ROOT/'dist/catalog.json').read_bytes();count=validate(json.loads(raw));digest=hashlib.sha256(raw).hexdigest()
url='https://cdn.jsdelivr.net/gh/daoshi818-crypto/chiyoushu-food-data@'+args.commit+'/dist/catalog.json'
for attempt in range(8):
 try:
  with urllib.request.urlopen(url,timeout=60) as r: downloaded=r.read(15*1024*1024+1)
  assert len(downloaded)==len(raw) and hashlib.sha256(downloaded).hexdigest()==digest
  break
 except Exception:
  if attempt==7:raise
  time.sleep(15)
try:
 with urllib.request.urlopen('https://daoshi818-crypto.github.io/chiyoushu-food-data/manifest.json',timeout=20) as r: old=json.load(r)
 assert args.sequence>old['release_seq'],'release_seq must increase'
except urllib.error.HTTPError as e:
 if e.code!=404:raise
m={'manifest_version':1,'dataset_id':'chiyoushu-cn-foods','release_seq':args.sequence,'catalog_version':datetime.datetime.now(datetime.timezone.utc).strftime('%Y.%m.%d.')+str(args.sequence),'catalog_schema_version':1,'published_at':datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z'),'source_commit':args.commit,'file':{'path':'dist/catalog.json','sha256':digest,'bytes':len(raw),'food_count':count}}
(ROOT/'site/manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(m,ensure_ascii=False))
