from abc import abstractmethod
from typing import Any, Callable, Dict, List, Mapping, Sequence, SupportsIndex, Type, Union
import json, yaml
import os

CONFIG = {
	"delim": ".",
	"use_delimited_keys": True,
}

dicty_config_file = os.environ.get("DICTY_CONFIG_FILE", ".dicty-config.json")
if os.path.exists(dicty_config_file):
	with open(dicty_config_file, "r") as f:
		config = json.load(f)
		CONFIG.update(config)


class Dicty:
	def __new__(cls, data=None, **kwargs):

		parent = kwargs.pop('__parent', None)
		key = kwargs.pop('__key', None)
		type = kwargs.pop('__type', None)

		if data is None:
			d = object.__new__(DictyEmpty, **kwargs)
		elif isinstance(data, Mapping):
			d = DictyDict.__new__(DictyDict, data, **kwargs)
		elif isinstance(data, List):
			d = DictyList.__new__(DictyList, data, **kwargs)
		else:
			raise ValueError("unsupported constructor argument {}".format(arg))
		
		object.__setattr__(d, '__parent', parent)
		object.__setattr__(d, '__key', key)
		object.__setattr__(d, '__type', type)
		
		return d

	def set_type(self, type: Type):
		object.__setattr__(self, '__type', type)
	
	### UTILS
	def _check_value(self, v):
		try:
			dicty_type = object.__getattribute__(self, '__type')
		except AttributeError:
			dicty_type = None

		if isinstance(v, Dicty):
			return v	
		elif isinstance(v, Mapping) or isinstance(v, List):
			return Dicty(v, __type=dicty_type)
		else:
			if dicty_type is not None and not isinstance(v, dicty_type):
				raise TypeError("Trying to add an item of type {} to a Dicty of type {}".format(type(v), dicty_type))
			return v

	### CREATION
	@staticmethod
	def from_json(path: str):
		with open(path, "r") as f:
			return Dicty(json.load(f))

	@staticmethod
	def from_yaml(path: str):
		with open(path, "r") as f:
			return Dicty(yaml.load(f))

	@staticmethod
	def from_file(path: str):
		if path.endswith(".json"):
			return Dicty.from_json(path)
		elif path.endswith(".yaml"):
			return Dicty.from_yaml(path)
		else:
			raise ValueError("Can only load from json or yaml")

	### OPERATIONS
	def rename_key(self, old_key_name, new_key_name):
		raise NotImplementedError()

	def to_plain(self) -> Union[dict, list]:
		if isinstance(self, DictyDict):
			return self.to_dict()
		elif isinstance(self, DictyList):
			return self.to_list()
		else:
			raise RuntimeError("Somewhing went very wrong here!")


class DictyDict(Dicty, dict):
	def __new__(cls, *args, **kwargs):
		return dict.__new__(cls, *args, **kwargs)
	
	def __init__(self, data: Mapping, **kwargs):
		# Dicty.__init__(self, data, **kwargs)
		# make these attributes private to Dicty so their dont mess with dict
		for k, v in data.items():
			self[k] = v

	def __setattr__(self, k, v):
		self.__setitem__(k, v)

	def __getattr__(self, k):
		return self[k]

	def __getitem__(self, k):
		recursed, item = self.__recurse_key(DictyDict.__getitem__, k)
		if recursed:
			return item
		else:
			return dict.__getitem__(self, k)

	def __missing__(self, k):
		return Dicty({}, __parent=self, __key=k)

	def __setitem__(self, k, v) -> None:
		if self.__recurse_key(DictyDict.__setitem__, k, v)[0]:
			return

		v = self._check_value(v)

		dict.__setitem__(self, k, v)

		try:
			p = object.__getattribute__(self, '__parent')
			k = object.__getattribute__(self, '__key')
		except AttributeError:
			p = None
			k = None
		
		if p and k:
			p[k] = self
			object.__delattr__(self, '__parent')
			object.__delattr__(self, '__key')

	def __delattr__(self, key: str) -> None:
		return self.__delitem__(key)

	def __delitem__(self, k) -> None:
		if not self.__recurse_key(DictyDict.__delitem__, k)[0]:
			return dict.__delitem__(self, k)

	def __recurse_key(self, fn, k, *args, **kwargs) -> bool:
		ks = k.split(CONFIG["delim"], 1)
		if len(ks) > 1:
			rets = fn(self[ks[0]], ks[1], *args, **kwargs)
			return True, rets
		else:
			return False, None
	
	def slice(self, s: slice):
		try:
			type = object.__getattribute__(self, '__type')
		except Exception:
			type = None
		base = Dicty({}, __type=type)
		for key, value in self.items():
			if isinstance(value, DictyDict) or isinstance(value, DictyList):
				base[key] = value.slice(s)
			else:
				base[key] = value[s]
		return base
		
	def flattened(self, prefix="") -> dict:
		base = {}
		delim = CONFIG["delim"]
		for key, value in self.items():
			if isinstance(value, Dicty):
				for k, v in value.flattened(prefix=prefix+delim+key).items():
					base[k] = v
			else:
				base[prefix+delim+key] = value
		return base

	def to_dict(self) -> dict:
		base = {}
		for k, v in self.items():
			if isinstance(v, Dicty):
				base[k] = v.to_plain()
			else:
				base[k] = v
		return base
	
	def leafs(self) -> List[Any]:
		res = []
		for v in self.values():
			if isinstance(v, Dicty):
				res += v.leafs()
			else:
				res.append(v)
		return res

	def update(self, *args, **kwargs):
		if len(args) > 1:
			raise TypeError()
		other = args[0] if len(args) == 1 else {}
		other.update(kwargs)

		for k, v in other.items():
			if k in self:
				if isinstance(self[k], dict):
					assert isinstance(v, dict)
					self[k].update(v)
				elif isinstance(self[k], list):
					assert isinstance(v, list)
					assert len(self[k]) == len(v)
					self[k].update(v)
				else:
					self[k] = v
			else:
				v = self._check_value(v)
				self[k] = v	

	def __getnewargs__(self):
		return (self.to_dict(),)


class DictyList(Dicty, list):
	def __new__(cls, args: List, **kwargs):
		return list.__new__(cls, *args, **kwargs)
	
	def __init__(self, data: List, **kwargs):
		# Dicty.__init__(self, data, **kwargs)
		for x in data:
			self.append(x)

	def __setitem__(self, idx: int, v):
		v = self._check_value(v)
		list.__setitem__(self, idx, v)

	def __getitem__(self, key: Union[int, slice, Any]):
		if isinstance(key, tuple):
			raise NotImplementedError()
		elif isinstance(key, int) or isinstance(key, slice):
			return list.__getitem__(self, key)
		else:
			# if the key is obviously not an index into the list, try
			# to use it as a key for all dicts in the list(s)
			return [x[key] if isinstance(x, Dicty) else None for x in self]

	def __setitem__(self, key, value):
		if isinstance(key, tuple):
			raise NotImplementedError()
		elif isinstance(key, int) or isinstance(key, slice):
			return list.__setitem__(self, key, value)
		else:
			# if the key is obviously not an index into the list, try
			# to use it as a key for all dicts in the list(s)
			for x in self:
				if isinstance(x, Dicty):
					x[key] = value

	def append(self, v) -> None:
		v = self._check_value(v)
		list.append(self, v)

	def __delitem__(self, i: Union[SupportsIndex, slice]) -> None:
		return list.__delitem__(self, i)
	
	def insert(self, idx: SupportsIndex, v) -> None:
		v = self._check_value(v)
		return list.insert(idx, v)

	def slice(self, s: slice):
		try:
			type = object.__getattribute__(self, '__type')
		except Exception:
			type = None
		base = Dicty([], __type=type)
		for value in self:
			if isinstance(value, Dicty):
				base.append(value.slice(s))
			else:
				base.append(value[s])
		return base
		
	def flattened(self, prefix="") -> dict:
		base = {}
		delim = CONFIG["delim"]
		for idx, value in enumerate(self):
			new_key = prefix+'['+str(idx)+']'
			if isinstance(value, Dicty):
				for k, v in value.flattened(prefix=new_key).items():
					base[k] = value
			else:
				base[new_key] = value
		return base

	def to_list(self) -> list:
		base = []
		for x in self:
			if isinstance(x, Dicty):
				base.append(x.to_plain())
			else:
				base.append(x)
		return base
	
	def leafs(self) -> List[Any]:
		res = []
		for v in self:
			if isinstance(v, Dicty):
				res += v.leafs()
			else:
				res.append(v)
		return res

	def update(self, other):
		if not isinstance(other, list):
			raise TypeError()
		assert len(other) == len(self)
		for i, x, xx in zip(range(len(self)), self, other):
			if isinstance(x, dict):
				assert isinstance(xx, dict)
				x.update(xx)
			elif isinstance(x, list):
				assert isinstance(xx, list)
				x.update(xx)
			else:
				self[i] = xx


class DictyEmpty(Dicty):
	def __new__(cls, *args, **kwargs):
		return object.__new__(cls, *args, **kwargs)

	def __init__(self):
		pass


### OPERATIONS	
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
