from .dicty import Dicty, DictyDict, DictyList
from typing import Callable, Any, List, Dict, Union

def apply(op: Callable, *op_args: Dicty, _dictoo_apply_is_leaf_rule: Union[Callable[[Any], bool], None] = None, _dictoo_apply_nested_key: List[str] = [], **op_kwargs: Any) -> Dicty:
	"""Apply an n-ary operation to n dicts.

	The Dictys need to either provide defaults or have a matching structure.
	The op is called with the values from each dict under the same path.

	Args:
		op (Callable): the callable that works under 
	Retrusn: 
	"""
	if _dictoo_apply_is_leaf_rule and _dictoo_apply_is_leaf_rule(op_args[0]):
		res = op(*op_args, _dictoo_key=_dictoo_apply_nested_key, **op_kwargs)
	
	elif isinstance(op_args[0], DictyList):
		res = DictyList([])
		lens = [len(x) for x in op_args]
		assert min(lens) == max(lens) # assert all equal length
		for i in range(len(op_args[0])):
			res.append(apply(
				op,
				*[op_arg[i] for op_arg in op_args],
				_dictoo_apply_is_leaf_rule=_dictoo_apply_is_leaf_rule, _dictoo_apply_nested_key=_dictoo_apply_nested_key + [str(i)],
				**op_kwargs
			))

	elif isinstance(op_args[0], DictyDict):
		res = DictyDict({})
		for k in op_args[0]:
			res[k] = apply(
				op,
				*[op_arg[k] for op_arg in op_args],
				_dictoo_apply_is_leaf_rule=_dictoo_apply_is_leaf_rule, _dictoo_apply_nested_key=_dictoo_apply_nested_key + [k],
				**op_kwargs
			)

	elif _dictoo_apply_is_leaf_rule is None:  # leaf case
		res = op(*op_args, _dictoo_key=_dictoo_apply_nested_key, **op_kwargs)
	
	else: #not a leaf according to is_leaf_rule but also not a nested Dicty
		raise RuntimeError("not a leaf according to is_leaf_rule but also not a nested Dicty")
	
	return res

def foreach(op: Callable[[any, List[Union[int,str]]], None], data: any, key: List[Union[int, str]] = []) -> None:
	"""Iterate over the leaf values and optionally keys of a dicty.

	Args:
		op (Callable): the callable that works under 
	Retrusn: 
	"""
	if isinstance(data, DictyList):
		for i in range(len(data)):
			foreach(op, data[i], key + [i])

	elif isinstance(data, DictyDict):
		for k in data:
			foreach(op, data[k], key + [k])

	else:  # leaf case
		op(data, tuple(key))


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
	

def slice(d, s: slice, _dictoo_apply_is_leaf_rule: Union[Callable[[Any], bool], None] = None):
	try:
		type = object.__getattribute__(d, '__type')
	except Exception:
		type = None
	if isinstance(d, DictyList):
		base = Dicty([], __type=type)
		for value in d:
			if _dictoo_apply_is_leaf_rule and _dictoo_apply_is_leaf_rule(value):
				base.append(value[s])
			elif isinstance(value, Dicty):
				base.append(slice(value, s))
			elif _dictoo_apply_is_leaf_rule is None:
				base.append(value[s])
			else:
				raise RuntimeError()
		return base
	elif isinstance(d, DictyDict):
		base = Dicty({}, __type=type)
		for key, value in d.items():
			if _dictoo_apply_is_leaf_rule and _dictoo_apply_is_leaf_rule(value):
				base[key] = value[s]
			elif isinstance(value, DictyDict) or isinstance(value, DictyList):
				base[key] = slice(value, s)
			elif _dictoo_apply_is_leaf_rule is None:
				base[key] = value[s]
			else:
				raise RuntimeError()
	else:
		raise ValueError()

	return base
	
