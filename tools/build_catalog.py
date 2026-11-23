import json,hashlib,pathlib,math
from classify_foods import prepare, classify
ROOT=pathlib.Path(__file__).resolve().parents[1]
def validate(data):
 assert data['schema_version']==1 and data['foods']
 ids=set()
 categories=data.get('categories')
 if categories is not None:
  assert 0<len(categories)<=64
  category_ids={c['id'] for c in categories}
  assert len(category_ids)==len(categories)
  for category in categories:
   assert category['id'] and category['label'].strip() and len(category['label'])<=24
 for f in data['foods']:
  assert f['id'] and f['id'] not in ids,(f['name'],'duplicate id')
  ids.add(f['id'])
  if categories is not None:assert f.get('category_id') in category_ids
  assert f['name'].strip() and f['unit'] in ('g','ml') and f['sources']
  assert all(v is None or isinstance(v,(int,float)) and math.isfinite(v) and v>=0 for v in f['nutrients'].values())
  weights=[p['grams'] for p in f['portions']]
  assert len(weights)==len(set(weights)) and all(math.isfinite(v) and 0<v<=10000 for v in weights)
 return len(ids)
def build():
 foods=[json.loads(line) for line in (ROOT/'source/foods.jsonl').read_text(encoding='utf8').splitlines() if line.strip()]
 config=json.loads((ROOT/'source/categories.json').read_text(encoding='utf8'))
 rules=prepare(config)
 assert set(config['overrides']) <= {food['id'] for food in foods}
 for f in foods:
  f['category_id']=classify(f,config,rules)
  payload={k:v for k,v in f.items() if k!='revision'}
  f['revision']=hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:16]
 data={'schema_version':1,'categories':config['categories'],'foods':sorted(foods,key=lambda f:f['id'])}
 count=validate(data)
 raw=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode()
 assert len(raw)<=15*1024*1024
 (ROOT/'dist/catalog.json').write_bytes(raw)
 print(json.dumps({'food_count':count,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}))
if __name__=='__main__':build()
