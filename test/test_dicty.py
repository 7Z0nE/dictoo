import pytest
from typing import Dict
import dictoo as dt
import json, yaml, os, sys

from dictoo.dicty import DictyDict

# try:
# 	torch = __import__('torch')
# except Exception:
# 	pytest.skip("Cannot test with torch because it is not installed")
# try:
# 	np = __import__('numpy')
# except Exception:
# 	pytest.skip("Cannot test with numpy because it is not installed")


@pytest.fixture
def empty_dictydict():
	return dt.Dicty({})

@pytest.fixture
def empty_dictylist():
	return dt.Dicty([])

@pytest.fixture
def simple_nested_dict():
	return {
		'a': 1,
		'b': {
			'c': 5
		}
	}

@pytest.fixture
def simple_dict():
	return {'a': 1, 'b': 2}

@pytest.fixture
def list_of_dicts():
	return [{'a': 1, 'b': 2} for _ in range(3)]

@pytest.fixture
def list_of_list_of_dicts():
	return [[{'a': 1, 'b': 2} for _ in range(3)] for _ in range(3)]

@pytest.fixture
def dict_with_list_of_dicts():
	return {
		'l': [
			{'a': 1, 'b': 2},
			{'a': 2, 'b': 3},
			{'a': 3, 'b': 4}
		],
		'm': 5
	}

@pytest.fixture
def  list_of_different_dicts():
	return [{'a': 1, 'b': 2}, {'a':3, 'c':4}, {'a':5, 'd': 6, 'e': 7}]

@pytest.fixture
def nested_dict_same_key():
	return {'a': {'a': {'a': 3}}}


def test_constructor_and_to_plain(simple_dict, list_of_dicts, dict_with_list_of_dicts, list_of_different_dicts):
	assert simple_dict == dt.Dicty(simple_dict).to_plain()
	assert list_of_dicts == dt.Dicty(list_of_dicts).to_plain()
	assert dict_with_list_of_dicts == dt.Dicty(dict_with_list_of_dicts).to_plain()
	assert list_of_different_dicts == dt.Dicty(list_of_different_dicts).to_plain()

def test_construct_from_json(simple_nested_dict, tmpdir):
	file = os.path.join(tmpdir, "test.json")
	with open(file, "w+") as f:
		json.dump(simple_nested_dict, f)

	d = dt.Dicty.from_file(file)

	assert d.to_dict() == simple_nested_dict


def test_construct_from_yaml(simple_nested_dict, tmpdir):
	file = os.path.join(tmpdir, "test.yaml")
	with open(file, "w+") as f:
		yaml.dump(simple_nested_dict, f)

	d = dt.Dicty.from_file(file)

	assert d.to_dict() == simple_nested_dict

def test_get_nested(simple_nested_dict):
	d = dt.Dicty(simple_nested_dict)
	assert simple_nested_dict["b"]["c"] == d["b"]["c"]
	assert simple_nested_dict["b"]["c"] == d.b.c
	assert simple_nested_dict["b"]["c"] == d["b.c"]

def test_set_new_key_nested(simple_nested_dict):
	d = dt.Dicty(simple_nested_dict)
	d["g"] = 1
	d["b"]["d"] = 2
	d["h.j"] = 3
	assert d["g"] == 1
	assert d["b"]["d"] == 2
	assert d["h.j"] == 3

	d = dt.Dicty(simple_nested_dict)
	d.g = 1
	d.b.d = 2
	d.h.j = 3
	
	assert d.g == 1
	assert d.b.d == 2
	assert d.h.j == 3

def test_constructor_copies(simple_nested_dict):
	d = dt.Dicty(simple_nested_dict)
	d.a += 1
	d.b.c += 1

	assert d.a == simple_nested_dict["a"] + 1
	assert d.b.c == simple_nested_dict["b"]["c"] + 1

def test_typed_dict(simple_nested_dict):
	d = dt.Dicty(simple_nested_dict, __type=int)
	d.d = 8
	with pytest.raises(TypeError) as e:
		d.e = "u"

def test_append(list_of_dicts):
	d = dt.Dicty(list_of_dicts)
	items = [[0], {'a': 1}, dt.Dicty({'b': 1}), []]
	for i in items:
		d.append(i)
	d[-1].append(dt.Dicty({'a': 1}))

def test_batched_getitem(list_of_dicts, list_of_list_of_dicts):
	d = dt.Dicty(list_of_dicts)
	assert d['a'] == dt.Dicty([dd['a'] for dd in d])
	d = dt.Dicty(list_of_list_of_dicts)
	assert d['a'] == dt.Dicty([ddd['a'] for dd in d for ddd in dd])

def test_batched_setitem(list_of_dicts, list_of_list_of_dicts):
	d = dt.Dicty(list_of_dicts)
	d['a'] = 10
	assert sum(d['a']) == 10*len(d)
	d[:2]['a'] = 1
	assert sum(d['a']) == 2 * 1 + (len(d)-2) * 10
	d = dt.Dicty(list_of_list_of_dicts)
	d['a'] = 10
	assert sum(d['a']) == 10*len(d)*len(d[0])

def test_leafs(empty_dictydict, empty_dictylist):
	d = dt.Dicty({'a': 1, 'b': 2, 'c':{'d': 3, 'e': [4,5], 'f': 6}})
	assert [1,2,3,4,5,6] == d.leafs()
	assert [] == empty_dictydict.leafs()
	assert [] == empty_dictydict.leafs()

def test_apply():
	d = dt.Dicty({'str': 'h', 'int':5, 'float': 0.5})
	d_types = dt.Dicty({'str': str, 'int': int, 'float': float})
	res = dt.apply(isinstance, d, d_types)
	assert res == dt.Dicty({'str': True, 'int': True, 'float': True})

def test_reduce(simple_dict):
	reduced = dt.reduce(sum, [dt.Dicty(simple_dict), dt.Dicty(simple_dict), dt.Dicty(simple_dict)])
	calculated = dt.apply(lambda x: x*3, dt.Dicty(simple_dict))
	assert reduced == calculated

def test_foreach(simple_nested_dict):
    d = dt.Dicty(simple_nested_dict)
    flat_items = list(d.flattened().items())
    def fn(v, k):
        flat_items.remove([k, v])
    assert len(flat_items) == 0 

def test_reduce(simple_dict):
	reduced = dt.reduce(sum, [dt.Dicty(simple_dict), dt.Dicty(simple_dict), dt.Dicty(simple_dict)])
	calculated = dt.apply(lambda x: x*3, dt.Dicty(simple_dict))
	assert reduced == calculated

def test_search(simple_nested_dict, list_of_different_dicts, nested_dict_same_key):
	d = dt.Dicty(simple_nested_dict)
	assert d.search('c') == 5
	d = dt.Dicty(list_of_different_dicts)
	assert d.search('a') == 1
	assert d.search('c') == 4
	d = dt.Dicty(nested_dict_same_key)
	assert d.search('a') == 3
	with pytest.raises(KeyError):
		d.search('u')

def test_flatten(simple_nested_dict, list_of_different_dicts, dict_with_list_of_dicts):
	d = dt.Dicty(simple_nested_dict)
	d_flat = d.flattened()
	assert d_flat['b.c'] == d['b']['c']
	assert d_flat['a'] == d['a']
	
	d = dt.Dicty(list_of_different_dicts)
	d_flat = d.flattened()
	assert d_flat['[0].a'] == 1
	assert d_flat['[1].a'] == 2
	assert d_flat['[2].b'] == 4

	d = dt.Dicty(list_of_different_dicts)
	d_flat = d.flattened()

@pytest.mark.skipif('numpy' not in sys.modules, reason="Skipping numpy tests because numpy is not installed.")
class TestNumpy:
	@pytest.fixture
	def dicts(self):
		return dt.Dicty([{
					'a': np.random.normal(0, 1, (3, 4)),
					'b': np.random.normal(2, 1, (2,)),
					'c': {
						'ca': np.random.normal(3, 1, (3,)),
						'cb': [
							np.random.normal(4, 1, (3, 3)),
							np.random.normal(4, 1, (3, 3)),
						]
					}
				} for i in range(3)])
	
	def test_apply(self):
		arrays = [np.random.normal(0, 1, (3, 4)), np.random.normal(2, 1, (2,)), np.random.normal(4, 1, (3, 3))]
		d = dt.Dicty({'a': arrays[0], 'b': arrays[1:]})
		d_res = dt.Dicty({'a': np.sum(arrays[0], axis=0), 'b': [np.sum(arrays[1], axis=0), np.sum(arrays[2], axis=0)]})
		assert dt.apply(np.sum, d, axis=0) == d_res

	@pytest.mark.skip('No skip reason')
	def test_reduce(self, dicts):
		print("np.stack: {}".format(dt.reduce(np.stack, dicts)))
		print("np.concat: {}".format(dt.reduce(np.concatenate, dicts, axis=-1)))
	
	@pytest.mark.skip('No skip reason')
	def test_slice(self, dicts):
		print("slice: {}".format(dicts[0].slice((0))))


@pytest.mark.skipif('torch' not in sys.modules, reason="Skipping torch tests because pytorch is not installed.")
class TestTorch:
	@pytest.fixture
	def dicts(self):
		return dt.Dicty([{
					'a': torch.normal(0, 1, (3, 4)),
					'b': torch.normal(2, 1, (2,1)),
					'c': {
						'ca': torch.normal(3, 1, (3,1)),
						'cb': [
							torch.normal(4, 1, (3, 3)),
							torch.normal(4, 1, (3, 3)),
						]
					}
				} for i in range(3)])

	@pytest.mark.skip
	def test_apply(self, dicts):
		print("torch.sum: {}".format(dt.apply(torch.sum, dicts[0], axis=0)))
		print("torch.dot: {}".format(dt.apply(torch.matmul, dicts[0], dt.apply(torch.transpose, dicts[1], dim0=0, dim1=1))))
	
	@pytest.mark.skip
	def test_reduce(self, dicts):
		print("torch.stack: {}".format(dt.reduce(torch.stack, dicts)))
		print("torch.cat: {}".format(dt.reduce(torch.cat, dicts, axis=-1)))

	@pytest.mark.skip
	def test_slice(self, dicts):
		print("slice: {}".format(dicts[0].slice((1, 0))))
