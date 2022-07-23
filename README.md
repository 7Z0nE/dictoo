# DICTionary Operations
Is a library that makes applying functions to and performing operations on nested dicts easy.

This repository attempts to unify numerous utilities in one package.

Python >=3.7 is required as retained dict order is wanted.

Python library that inspired this project:
# TODO: links
https://github.com/glowdigitalmedia/dict-utils/tree/master/dict_utils
 - https://github.com/katsudonik/dict_util
 - https://github.com/gmr/flatdict/blob/master/flatdict.py
 - https://github.com/bunbun/nested-dict
 - https://github.com/jacobflanagan/nesteddictionary
 - https://github.com/ducdetronquito/scalpl
 - https://github.com/mewwts/addict
 - https://github.com/zphang/sndict
 - https://github.com/nickstanisha/nesteddict
 - https://github.com/bunbun/nested-dict

# Features
Scalpl seems to be the most polished library. Dicty differs with some slight changes in the api
and additional set of functionality for operating on json like data structure:
- apply an operation to multiple dictoos with same shape
- setting the type for the dictoos values

# Setup

	pip install dictoo

# Usage


	import dictoo.Dicty as D

	# you can configure dictoo to fit your needs
	# dictoo only imports and uses what is enabled
	dictoo.CONFIG.update({
		'delimiter': '.'
	})

	# you can create dictoo dicts from many things
	d = D(dict(a=1, b=[3, dict(c=4)]))
	d = D.from_file('dict.yaml')
	d = D.from_file('dict.json')
	d = D("{a:1, b[0]:3, b[1].c=4}")  //not sure whether this is a good idea

	assert d.b[1].c == d['b.[1].c']

	d.update(dict(b=[5, dict(c=9)]))

	d.flat()

	dictoo.apply(lambda x, y: x + y, d1, d2, kwargs)
	
	dictoo.reduce(fn, [d1, d2, d3], kwargs)

	dictoo.remap({'old_key_name': 'new_key_name'})

	d = D([{'a': 1, 'b': 2}, {'a':4, 'b':5})
	isinstance(d, list) == True
	isinstance(d, dict) == False
	assert d != [D({'a': 1, 'b': 2}), D({'a':4, 'b':5})]  # try not to leave lists of Ds as you would also not do with numpy arrays
	assert d == D([D({'a': 1, 'b': 2}), D({'a':4, 'b':5})])
	d[:, 'a'] = 8  # D([{'a': 8, 'b': 2}, {'a':8, 'b':5}])  # this is hard to get used to, maybe be more strict here such that the code is more readable. Should be configurable
	d[:1, 'a'] = 8  # only modifies a slice

	d.batch()['a'][:] = 8

	d: Dict[str, Union[np.ndarray, dict]] = D(dict(...), dtype=np.ndarray)

	d.batch()  # D({'a': [1, 4], 'b': [2, 5]}), batch goes from lowest level to top level and unbatch inreverse

	# more features:
	# cli for json and yaml files
	# regex keys
