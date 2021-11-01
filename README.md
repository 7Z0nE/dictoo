# DICTionary OPerations
Is a library that makes applying functions to and performing operations on nested dicts easy.

This repository attempts to unify numerous utilities in one package.

Python >=3.7 is required as retained dict order is wanted.

# TODO: links
 - dict-util
 - dict-utils
 - flatdict
 - nested_dict
 - nested-dictionaries
 - scalpl
 - https://github.com/mewwts/addict
 - https://github.com/zphang/sndict
 - https://github.com/nickstanisha/nesteddict
 - https://github.com/bunbun/nested-dict
 - dictop

# Features
Looking at existing dict utils we can collect a list of utilities that people are interested in:
 - manipulating dicts with _setattr
 - flattening dicts
 - searching dicts
 - updating dicts with other dicts
 - default value
 - operating on dict values parallely (ours)

# Usage

	from dicty import D

	# you can configure dicty to fit your needs
	# dicty only imports and uses what is enabled
	dicty.config({
		'delimiter': '.',
		'enable_numpy': true
	})

	# you can create dicty dicts from many things
	d = D(dict(a=1, b=[3, dict(c=4)]))
	d = D.from_file('dict.yaml')
	d = D.from_file('dict.json')
	d = D("{a:1, b[0]:3, b[1].c=4}")  //not sure whether this is a good idea

	assert d.b[1].c == d['b[1].c']

	d.update(dict(b=[5, dict(c=9)]))

	d.flat()

	dicty.apply(+, d1, d2, kwargs)
	
	dicty.reduce(fn, [d1, d2, d3], kwargs)

	dicty.remap({'old_key_name': 'new_key_name'})

	d = D([{'a': 1, 'b': 2}, {'a':4, 'b':5})
	d.is_list() == True
	d.is_dict() == False
	assert d != [D({'a': 1, 'b': 2}), D({'a':4, 'b':5})]  # try not to leave lists of Ds as you would also not do with numpy arrays
	assert d == D([D({'a': 1, 'b': 2}), D({'a':4, 'b':5})])
	d['a'] = 8  # D([D({'a': 8, 'b': 2}), D({'a':8, 'b':5})])  # this is hard to get used to, maybe be more strict here such that the code is more readable. Should be configurable
	d[:]['a'] = 8  # same but more verbose
	d[:].a = 8
	d[:1]['a'] = 8  # only modifies a slice

	d.batch()['a'][:] = 8

	d: Dict[str, Union[np.ndarray, dict]] = D(dict(...), dtype=np.ndarray)

	d.batch()  # D({'a': [1, 4], 'b': [2, 5]}), batch goes from lowest level to top level and unbatch inreverse

	# more features:
	# cli for json and yaml files
	# regex keys
