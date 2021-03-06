import inspect
from enum import Enum as BaseEnum, IntEnum as BaseIntEnum
from enum import EnumMeta as BaseEnumMeta
from enum import _EnumDict


try:
	from flex.utils.decorators import export
except ImportError:
	def export(obj):
		__all__.append(obj.__name__)
		return obj


__all__ = []


class EnumMeta(BaseEnumMeta):
	def __new__(mcs, name, bases, attrs):
		Labels = attrs.get('Labels')

		if Labels is not None and inspect.isclass(Labels):
			del attrs['Labels']
			if hasattr(attrs, '_member_names'):
				attrs._member_names.remove('Labels')

		obj = BaseEnumMeta.__new__(mcs, name, bases, attrs)
		for m in obj:
			try:
				m.label = getattr(Labels, m.name)
			except AttributeError:
				m.label = m.name.lower()

		return obj

	def choices(cls):
		return tuple((m, m.label) for m in cls)

	# def __getitem__(cls, key):
	# 	try:
	# 		return super(EnumMeta, cls).__getitem__(key)
	# 	except KeyError as e:
	# 		try:
	# 			return super(EnumMeta, cls).__getitem__(str(key).upper())
	# 		except KeyError:
	# 			raise e

	def __repr__(self):
		return '%s' % (self.__name__)


@export
class Enum(EnumMeta('Enum', (BaseEnum,), _EnumDict())):
	__slots__ = ('label',)

	# def __repr__(self):
	# 	return '%s(%r)' % (self, self.value)


@export
class IntEnum(EnumMeta('IntEnum', (BaseIntEnum,), _EnumDict())):
	__slots__ = ()
	# def __repr__(self):
	# 	return '%s(%r)' % (self, self.value)


@export
class StrEnum(EnumMeta('StrEnum', (str, BaseEnum), _EnumDict())):
	__slots__ = ()

	def __str__(self):
		return self.value
