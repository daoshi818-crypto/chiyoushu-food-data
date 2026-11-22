from build_catalog import ROOT,validate
import json
print(validate(json.loads((ROOT/'dist/catalog.json').read_text(encoding='utf8'))))
