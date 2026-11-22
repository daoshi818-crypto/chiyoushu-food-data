import json,hashlib,pathlib,math
ROOT=pathlib.Path(__file__).resolve().parents[1]
def validate(data):
 assert data['schema_version']==1 and data['foods']
 ids=set()
 for f in data['foods']:
  assert f['id'] and f['id'] not in ids,(f['name'],'duplicate id')
  ids.add(f['id'])
  assert f['name'].strip() and f['unit'] in ('g','ml') and f['sources']
  assert all(v is None or isinstance(v,(int,float)) and math.isfinite(v) and v>=0 for v in f['nutrients'].values())
  weights=[p['grams'] for p in f['portions']]
  assert len(weights)==len(set(weights)) and all(math.isfinite(v) and 0<v<=10000 for v in weights)
 return len(ids)
def build():
 foods=[json.loads(line) for line in (ROOT/'source/foods.jsonl').read_text(encoding='utf8').splitlines() if line.strip()]
 for f in foods:
  payload={k:v for k,v in f.items() if k!='revision'}
  f['revision']=hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:16]
 data={'schema_version':1,'foods':sorted(foods,key=lambda f:f['id'])}
 count=validate(data)
 raw=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode()
 assert len(raw)<=15*1024*1024
 (ROOT/'dist/catalog.json').write_bytes(raw)
 print(json.dumps({'food_count':count,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}))
if __name__=='__main__':build()
