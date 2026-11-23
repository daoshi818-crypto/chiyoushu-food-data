import copy
import json
import unittest
from build_catalog import ROOT, validate
from classify_foods import prepare, classify


class CategoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((ROOT / 'source/categories.json').read_text(encoding='utf8'))
        cls.rules = prepare(cls.config)

    def category(self, name, source='brand'):
        return classify({'id': 'test', 'name': name, 'category': source}, self.config, self.rules)

    def test_ingredient_words_do_not_override_distinct_products(self):
        for name in ['鸡蛋糕', '蛋黄酥', '奶茶', '玉米油', '花生油', '苹果干', '牛肉干', '鱼皮花生']:
            expected = 'oils-seasoning' if name in ('玉米油', '花生油') else 'snacks-drinks'
            self.assertEqual(self.category(name), expected, name)
        self.assertEqual(self.category('金枪鱼拌饭'), 'dishes')
        self.assertEqual(self.category('牛肉面'), 'dishes')
        self.assertEqual(self.category('西麦燕麦片'), 'staples')
        self.assertEqual(self.category('德运脱脂奶粉'), 'meat-eggs-dairy')
        self.assertEqual(self.category('神秘产品'), 'other')
        self.assertEqual(self.category('泡芙', '主食'), 'snacks-drinks')
        self.assertEqual(self.category('番茄炒饭', '蔬菜'), 'dishes')

    def test_original_specific_categories_and_manual_override_win(self):
        self.assertEqual(self.category('番茄', '蔬菜类及制品'), 'vegetables')
        changed = copy.deepcopy(self.config)
        changed['overrides']['test'] = 'fruits'
        self.assertEqual(classify({'id': 'test', 'name': '未知', 'category': 'brand'}, changed, self.rules), 'fruits')

    def test_all_foods_keep_identity_nutrition_and_portions(self):
        source = [json.loads(line) for line in (ROOT / 'source/foods.jsonl').read_text(encoding='utf8').splitlines() if line]
        data = json.loads((ROOT / 'dist/catalog.json').read_text(encoding='utf8'))
        self.assertEqual(validate(data), len(source))
        by_id = {f['id']: f for f in data['foods']}
        for original in source:
            actual = by_id[original['id']]
            for field in ('name', 'nutrients', 'portions', 'unit', 'sources'):
                self.assertEqual(original[field], actual[field], (original['id'], field))
        invalid = copy.deepcopy(data)
        invalid['foods'][0]['category_id'] = 'missing'
        with self.assertRaises(AssertionError):
            validate(invalid)


if __name__ == '__main__':
    unittest.main()
