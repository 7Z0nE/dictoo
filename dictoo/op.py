from .dicty import Dicty, DictyDict, DictyList
from typing import Callable, Any, List, Dict

def apply(op: Callable, *op_args: Dicty, **op_kwargs: Any) -> Dicty:
	"""Apply an n-ary operation to n dicts.

	The Dictys need to either provide defaults or have a matching structure.
	The op is called with the values from each dict under the same path.

	Args:
		op (Callable): the callable that works under 
	Retrusn: 
	"""
	if isinstance(op_args[0], DictyList):
		res = DictyList([])
		lens = [len(x) for x in op_args]
		assert min(lens) == max(lens) # assert all equal length
		for i in range(len(op_args[0])):
			res.append(apply(op, *[op_arg[i] for op_arg in op_args], **op_kwargs))

	elif isinstance(op_args[0], DictyDict):
		res = DictyDict({})
		for k in op_args[0]:
			res[k] = (apply(op, *[op_arg[k] for op_arg in op_args], **op_kwargs))

	else:  # leaf case
		res = op(*op_args, **op_kwargs)
	
	return res

def foreach(op: Callable[[any, List[int | str]], None], dicty: any, key: List[int | str] = []) -> Dicty:
	"""Iterate over the leaf values and optionally keys of a dicty.

	Args:
		op (Callable): the callable that works under 
	Retrusn: 
	"""
	if isinstance(dicty, DictyList):
		res = DictyList([])
		for i in range(len(dicty)):
			res.append(foreach(op, dicty[i], key + [i]))

	elif isinstance(dicty, DictyDict):
		res = DictyDict({})
		for k in dicty:
			res[k] = (foreach(op, dicyt[k], key + [k]))

	else:  # leaf case
		res = op(dicty, key)
	
	return res

def reduce(op, values: List, **op_kwargs):
	"""Reduce an array of dictys with a reduction operator.

	The Dictys need to either provide defaults or have a matching structure.
	The op is called with the values from each dict under the same path.

	Args:
		op (Callable): the callable that works under 
	Return: 
	"""
	if isinstance(values[0], DictyList):
		res = DictyList([])
		lens = [len(x) for x in values]
		assert min(lens) == max(lens) # assert all equal length
		for i in range(lens[0]):
			res.append(reduce(op, [v[i] for v in values], **op_kwargs))

	elif isinstance(values[0], DictyDict):
		res = DictyDict({})
		for k in values[0]:
			res[k] = reduce(op, [v[k] for v in values], **op_kwargs)

	else:  # leaf case
		res = op(values, **op_kwargs)
	
	return res
	

def slice(d, s: slice):
	try:
		type = object.__getattribute__(d, '__type')
	except Exception:
		type = None
	if isinstance(d, DictyList):
		base = Dicty([], __type=type)
		for value in d:
			if isinstance(value, Dicty):
				base.append(slice(value, s))
			else:
				base.append(value[s])
		return base
	elif isinstance(d, DictyDict):
		base = Dicty({}, __type=type)
		for key, value in d.items():
			if isinstance(value, DictyDict) or isinstance(value, DictyList):
				base[key] = slice(value, s)
			else:
				base[key] = value[s]
	else:
		raise ValueError()

	return base
	
