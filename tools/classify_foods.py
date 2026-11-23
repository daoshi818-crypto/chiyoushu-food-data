"""Build editable browsing groups without changing original food identities."""
import re


def prepare(config):
    categories = config['categories']
    ids = {category['id'] for category in categories}
    assert len(ids) == len(categories) and 'other' in ids
    for category in categories:
        assert re.fullmatch(r'[a-z][a-z0-9_-]{0,63}', category['id'])
        assert category['label'].strip() and len(category['label']) <= 24
    assert set(config['source_categories'].values()) <= ids
    assert set(config['overrides'].values()) <= ids
    rules = []
    for rule in config['rules']:
        assert rule['id'] in ids
        rules.append((rule['id'], re.compile(rule['pattern'], re.I)))
    return rules


def classify(food, config, rules):
    override = config['overrides'].get(food['id'])
    if override:
        return override
    name = food['name']
    for category_id, pattern in rules:
        if category_id in ('oils-seasoning', 'snacks-drinks', 'dishes') and pattern.search(name):
            return category_id
    original = config['source_categories'].get(food.get('category'))
    if original:
        return original
    for category_id, pattern in rules:
        if pattern.search(name):
            return category_id
    return 'other'
